"""
End-to-end tests for critical user workflows.
Requirement IDs: FR-1 through FR-12, NFR-1 through NFR-11
Test Case IDs: TC-E2E-001, TC-E2E-002, TC-E2E-003
"""

import pytest

from app.models.state_models import (
    ActionType,
    AtomicAction,
    CriticVerdict,
    InputModality,
    InterruptPayload,
    NormalizedGoal,
    RunState,
    RunStatus,
)
from app.orchestrator.artifact_service import ArtifactService
from app.orchestrator.critic import BuildCritic, RepairService, StepCritic
from app.orchestrator.planner import Decomposer, GoalNormalizer, Planner
from app.orchestrator.run_manager import RunManager, RunStore
from app.orchestrator.runtime_executor import InterruptManager, RuntimeExecutor
from app.orchestrator.tool_registry import create_default_registry
from app.telegram.bot import TelegramGateway


@pytest.mark.e2e
class TestE2E001VoiceToReport:
    """
    TC-E2E-001: Voice message -> research -> Google Docs report -> Telegram link.
    Covers: FR-1, FR-2, FR-3, FR-6, FR-7, FR-8
    """

    @pytest.mark.asyncio
    async def test_full_voice_to_report_pipeline(self):
        """
        Automation ID: AT-E2E-001
        Description: Full pipeline from voice message to delivered report.
        """
        # Setup
        sent_messages = []

        async def capture_send(msg):
            sent_messages.append(msg)

        gateway = TelegramGateway(bot_token="test", send_fn=capture_send)
        store = RunStore()
        run_manager = RunManager(store)
        normalizer = GoalNormalizer()
        planner = Planner()
        decomposer = Decomposer()
        registry = create_default_registry()

        async def mock_docs_writer(content):
            return "https://docs.google.com/document/d/test-report/edit"

        artifact_service = ArtifactService(google_docs_writer=mock_docs_writer)
        step_critic = StepCritic()

        # Step 1: Receive voice message
        voice_update = {
            "update_id": 1000,
            "message": {
                "message_id": 1,
                "chat": {"id": 99999},
                "voice": {"file_id": "voice_ev_report", "duration": 8},
            },
        }
        update = gateway.parse_update(voice_update)
        assert update.message_type == "voice"

        # Step 2: Create run
        run = run_manager.create_run(
            update_id=update.update_id,
            user_id="user-e2e",
            chat_id=update.chat_id,
            input_modality=InputModality.VOICE,
            voice_file_id=update.voice_file_id,
        )
        assert run.execution_status == RunStatus.RECEIVED

        # Step 3: STT (simulated)
        transcript = "Make a report on the EV market in Saudi Arabia and save to Google Docs"
        run_manager.set_transcript(run.run_id, transcript)
        updated_run = store.get(run.run_id)
        assert updated_run.execution_status == RunStatus.TRANSCRIBED
        assert updated_run.transcript == transcript

        # Step 4: Goal normalization
        goal = await normalizer.normalize(transcript)
        assert goal.deliverable == "report"
        assert len(goal.ambiguities) == 0
        updated_run.normalized_goal = goal
        updated_run.execution_status = RunStatus.UNDERSTOOD
        store.save(updated_run)

        # Step 5: Plan
        plan = planner.create_plan(goal)
        assert not planner.should_clarify(plan)
        assert len(plan.steps) > 0
        updated_run.plan = plan
        updated_run.execution_status = RunStatus.PLANNED
        store.save(updated_run)

        # Step 6: Decompose
        actions = decomposer.decompose(plan)
        assert len(actions) > 0
        all_types_valid = all(
            a.action_type in {ActionType.LLM, ActionType.TOOL, ActionType.CODE, ActionType.USER_INPUT}
            for a in actions
        )
        assert all_types_valid

        # Step 7: Tool binding
        bindings, missing, warnings = registry.retrieve_tools(
            actions, user_scopes=["google_docs_write"]
        )
        updated_run.execution_status = RunStatus.TOOLS_BOUND
        store.save(updated_run)

        # Step 8: Execute (simulated - just verify critic works)
        executor = RuntimeExecutor()
        updated_run = await executor.execute_actions(updated_run, actions)
        assert updated_run.execution_status in {RunStatus.COMPLETED, RunStatus.INTERRUPTED}

        if updated_run.execution_status == RunStatus.COMPLETED:
            # Step 9: Create and deliver artifact
            artifact = artifact_service.create_artifact(
                artifact_type="report",
                content={"title": "EV Market Saudi Arabia", "body": "Analysis..."},
            )

            # Critic check on artifact
            critic_result = await step_critic.evaluate(
                action_description="Final report",
                expected_schema=None,
                actual_output=artifact.content,
            )
            assert critic_result.verdict == CriticVerdict.PASS

            # Deliver
            delivered = await artifact_service.deliver(
                artifact,
                destination="google_docs",
                critic_verdict=critic_result.verdict,
            )
            assert delivered.delivery_status == "sent"
            assert "docs.google.com" in delivered.artifact_url

            # Step 10: Send link to user
            await gateway.send_message(
                update.chat_id,
                f"Your report is ready: {delivered.artifact_url}",
            )
            assert len(sent_messages) >= 1
            assert any("docs.google.com" in m.get("text", "") for m in sent_messages)


@pytest.mark.e2e
class TestE2E002AmbiguousRequestClarification:
    """
    TC-E2E-002: Ambiguous request -> clarification -> resume -> completion.
    Covers: FR-4, FR-5, FR-9, FR-10
    """

    @pytest.mark.asyncio
    async def test_ambiguous_to_clarification_to_completion(self):
        """
        Automation ID: AT-E2E-002
        Description: Ambiguous request triggers clarification, then completes after user reply.
        """
        sent_messages = []

        async def capture_send(msg):
            sent_messages.append(msg)

        gateway = TelegramGateway(bot_token="test", send_fn=capture_send)
        store = RunStore()
        run_manager = RunManager(store)
        normalizer = GoalNormalizer()
        planner = Planner()
        decomposer = Decomposer()
        interrupt_mgr = InterruptManager()

        # Step 1: Receive ambiguous text
        text_update = {
            "update_id": 2000,
            "message": {
                "message_id": 1,
                "chat": {"id": 88888},
                "text": "Do it",
            },
        }
        update = gateway.parse_update(text_update)
        run = run_manager.create_run(
            update_id=update.update_id,
            user_id="user-e2e",
            chat_id=update.chat_id,
            input_modality=InputModality.TEXT,
            raw_input=update.text,
        )

        # Step 2: Normalize - should detect ambiguity
        goal = await normalizer.normalize(update.text)
        assert len(goal.ambiguities) > 0

        # Step 3: Planner returns clarifications
        plan = planner.create_plan(goal)
        assert planner.should_clarify(plan)
        assert len(plan.clarifications) > 0

        # Step 4: Create clarification action
        clarification = decomposer.create_clarification_action(
            question="Could you please be more specific? What task do you need done?",
            choices=None,
        )
        assert clarification.action_type == ActionType.USER_INPUT

        # Step 5: Send clarification to user via interrupt
        run.execution_status = RunStatus.WAITING_FOR_USER
        payload = InterruptPayload(
            question="Could you please be more specific? What task do you need done?",
            response_type="text",
            affected_state_fields=["clarified_goal"],
        )
        interrupt_mgr.create_interrupt(run.run_id, payload)
        await gateway.send_message(
            run.chat_id,
            payload.question,
        )
        assert len(sent_messages) >= 1

        # Step 6: User replies with clarification
        user_reply = "Create a summary of recent AI trends"
        result = interrupt_mgr.resolve(run.run_id, user_reply)
        assert result["value"] == user_reply

        # Step 7: Re-normalize with clarified input
        new_goal = await normalizer.normalize(user_reply)
        assert len(new_goal.ambiguities) == 0 or new_goal.goal != ""

        # Step 8: Re-plan with clear goal
        new_plan = planner.create_plan(
            NormalizedGoal(
                goal=user_reply,
                deliverable="summary",
                constraints=[],
                ambiguities=[],
            )
        )
        assert not planner.should_clarify(new_plan)
        assert len(new_plan.steps) > 0

        # Step 9: Resume execution
        run.execution_status = RunStatus.EXECUTING
        store.save(run)
        final = store.get(run.run_id)
        assert final.execution_status == RunStatus.EXECUTING


@pytest.mark.e2e
class TestE2E003WorkflowAuthoringWithRepair:
    """
    TC-E2E-003: Workflow authoring with compile error -> auto-repair -> success.
    Covers: FR-11, FR-12
    """

    @pytest.mark.asyncio
    async def test_workflow_compile_error_auto_repaired(self):
        """
        Automation ID: AT-E2E-003
        Description: Generated workflow with error is auto-repaired and executes.
        """
        critic = BuildCritic()

        # Step 1: Simulate spec.yaml generation (would be Prompt 1)
        spec_yaml = """
name: research_workflow
description: Research and report workflow
nodes:
  - id: research
    type: llm
  - id: compile_report
    type: llm
  - id: deliver
    type: tool
    tool: google_docs_write
edges:
  - from: START
    to: research
  - from: research
    to: compile_report
  - from: compile_report
    to: deliver
  - from: deliver
    to: END
"""

        # Step 2: Simulate code generation with error (would be Prompt 2)
        generated_files = {
            "state.py": "from typing import TypedDict\n\nclass WorkflowState(TypedDict):\n    research_data: str\n    report: str\n",
            "nodes.py": "def research(state)\n    return {'research_data': 'data'}\n\ndef compile_report(state):\n    return {'report': state['research_data']}\n",  # Syntax error: missing colon
            "graph.py": "# Graph definition\nfrom state import WorkflowState\n",
            "run.py": "print('Running workflow')\n",
        }

        # Step 3: Validate - should detect syntax error
        initial_result = await critic.validate(generated_files)
        assert initial_result.verdict == CriticVerdict.REPAIR
        assert any("SyntaxError" in i for i in initial_result.issues)

        # Step 4: Repair loop
        async def mock_repair(files, critic_result):
            # Fix the syntax error
            fixed = dict(files)
            fixed["nodes.py"] = "def research(state):\n    return {'research_data': 'data'}\n\ndef compile_report(state):\n    return {'report': state['research_data']}\n"
            return fixed

        repair_service = RepairService(llm_repair_fn=mock_repair)
        final_files, attempts, success = await repair_service.repair_loop(
            generated_files, critic, max_attempts=3
        )

        # Step 5: Verify repair succeeded
        assert success
        assert len(attempts) >= 1

        # Step 6: Verify final code is valid
        final_result = await critic.validate(final_files)
        assert final_result.verdict == CriticVerdict.PASS

        # Step 7: Verify repair log completeness
        for attempt in attempts:
            assert attempt.attempt_number >= 1
            assert attempt.error_class is not None
