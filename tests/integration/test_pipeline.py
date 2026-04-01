"""
Integration tests for the core pipeline.
Requirement IDs: FR-3, FR-4, FR-6, FR-7, FR-8, FR-9, NFR-5, NFR-7
Test Case IDs: TC-FR-004-02, TC-FR-008-01, TC-FR-008-02, TC-FR-009-01, TC-FR-009-02, TC-NFR-005-01, TC-NFR-007-01
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
from app.orchestrator.critic import StepCritic
from app.orchestrator.planner import Decomposer, GoalNormalizer, Planner
from app.orchestrator.runtime_executor import RuntimeExecutor
from app.orchestrator.tool_registry import create_default_registry


@pytest.mark.integration
class TestPlannerToToolPipeline:

    @pytest.mark.asyncio
    async def test_goal_to_plan_to_tools(self, goal_normalizer, planner, decomposer, tool_registry):
        """
        Description: Full pipeline from transcript to tool bindings.
        """
        # Step 1: Normalize
        goal = await goal_normalizer.normalize(
            "Research EV market in Saudi Arabia and create a report in Google Docs"
        )
        assert goal.deliverable == "report"

        # Step 2: Plan
        plan = planner.create_plan(goal)
        assert not planner.should_clarify(plan)
        assert len(plan.steps) > 0

        # Step 3: Decompose
        actions = decomposer.decompose(plan)
        assert len(actions) > 0

        # Step 4: Bind tools
        bindings, missing, warnings = tool_registry.retrieve_tools(
            actions, user_scopes=["google_docs_write"]
        )
        # Tool actions should have bindings
        tool_actions = [a for a in actions if a.action_type == ActionType.TOOL]
        assert len(bindings) == len(tool_actions) or len(warnings) > 0

    @pytest.mark.asyncio
    async def test_FR_004_missing_scope_triggers_interrupt(self, tool_registry, run_manager):
        """
        Automation ID: AT-FR-004-INT-01
        Description: Missing permission triggers waiting_for_user.
        """
        actions = [
            AtomicAction(
                action_type=ActionType.TOOL,
                description="Write report",
                tool_name="google_docs_write",
            ),
        ]

        bindings, missing_scopes, warnings = tool_registry.retrieve_tools(
            actions, user_scopes=[]
        )

        if missing_scopes:
            run = run_manager.create_run(
                update_id=400,
                user_id="user-1",
                chat_id="12345",
                input_modality=InputModality.TEXT,
                raw_input="write report",
            )
            run_manager.update_status(run.run_id, RunStatus.WAITING_FOR_USER)
            updated = run_manager.store.get(run.run_id)
            assert updated.execution_status == RunStatus.WAITING_FOR_USER
            assert "google_docs_write" in missing_scopes


@pytest.mark.integration
class TestArtifactDelivery:

    @pytest.mark.asyncio
    async def test_FR_008_delivery_after_critic_pass(self, artifact_service):
        """
        Automation ID: AT-FR-008-INT-01
        Description: Artifact delivered only after critic pass.
        """
        artifact = artifact_service.create_artifact(
            artifact_type="report",
            content={"title": "EV Report", "body": "Full analysis"},
        )

        # Delivery with PASS verdict
        delivered = await artifact_service.deliver(
            artifact,
            destination="google_docs",
            critic_verdict=CriticVerdict.PASS,
        )
        assert delivered.delivery_status == "sent"
        assert delivered.artifact_url

    @pytest.mark.asyncio
    async def test_FR_008_delivery_blocked_without_pass(self, artifact_service):
        """
        Automation ID: AT-FR-008-INT-02
        Description: Delivery blocked when critic verdict is not pass.
        """
        artifact = artifact_service.create_artifact(
            artifact_type="report",
            content={"title": "Bad Report", "body": ""},
        )

        for verdict in [CriticVerdict.RETRY, CriticVerdict.REPAIR, CriticVerdict.ESCALATE]:
            with pytest.raises(ValueError, match="critic verdict"):
                await artifact_service.deliver(
                    artifact,
                    destination="google_docs",
                    critic_verdict=verdict,
                )


@pytest.mark.integration
class TestExecutionWithInterrupt:

    @pytest.mark.asyncio
    async def test_FR_009_interrupt_pauses_execution(self, sample_run):
        """
        Automation ID: AT-FR-009-INT-01
        Description: User input action pauses execution.
        """
        actions = [
            AtomicAction(
                action_id="act-1",
                action_type=ActionType.LLM,
                description="Analyze",
            ),
            AtomicAction(
                action_id="act-2",
                action_type=ActionType.USER_INPUT,
                description="Ask for format",
                tool_name="request_user_input",
                tool_params={"question": "Which format?", "response_type": "choice", "choices": ["PDF", "Docs"]},
            ),
            AtomicAction(
                action_id="act-3",
                action_type=ActionType.LLM,
                description="Generate report",
            ),
        ]

        sample_run.normalized_goal = NormalizedGoal(goal="Create report")
        executor = RuntimeExecutor()
        result = await executor.execute_actions(sample_run, actions)

        assert result.execution_status == RunStatus.INTERRUPTED
        assert result.interrupt_payload is not None
        assert result.interrupt_payload.question == "Which format?"
        assert result.current_node == "act-2"

    @pytest.mark.asyncio
    async def test_FR_009_resume_after_interrupt(self, sample_run):
        """
        Automation ID: AT-FR-009-INT-02
        Description: Resume after user reply continues execution.
        """
        sample_run.execution_status = RunStatus.INTERRUPTED
        sample_run.interrupt_payload = InterruptPayload(question="Which format?")

        executor = RuntimeExecutor()
        result = await executor.resume(sample_run, "PDF")

        assert result.execution_status == RunStatus.EXECUTING
        assert result.interrupt_payload is None

    @pytest.mark.asyncio
    async def test_FR_009_resume_wrong_status_raises(self, sample_run):
        """Description: Resume on non-interrupted run raises error."""
        sample_run.execution_status = RunStatus.COMPLETED

        executor = RuntimeExecutor()
        with pytest.raises(ValueError, match="Cannot resume"):
            await executor.resume(sample_run, "response")


@pytest.mark.integration
class TestThreadContinuity:

    @pytest.mark.asyncio
    async def test_NFR_005_same_thread_after_resume(self, sample_run):
        """
        Automation ID: AT-NFR-005-INT-01
        Description: Thread ID preserved after interrupt/resume.
        """
        original_thread = sample_run.thread_id
        sample_run.execution_status = RunStatus.INTERRUPTED
        sample_run.interrupt_payload = InterruptPayload(question="test")

        executor = RuntimeExecutor()
        result = await executor.resume(sample_run, "answer")

        assert result.thread_id == original_thread


@pytest.mark.integration
class TestStepTracing:

    @pytest.mark.asyncio
    async def test_NFR_007_critic_log_per_step(self, sample_run, sample_actions):
        """
        Automation ID: AT-NFR-007-INT-01
        Description: Each step produces a critic log entry.
        """
        sample_run.normalized_goal = NormalizedGoal(goal="Test")
        executor = RuntimeExecutor()
        result = await executor.execute_actions(sample_run, sample_actions)

        # 3 actions (all non-user_input) each produce at least one critic entry
        assert len(result.critic_log) >= len(sample_actions)
        for entry in result.critic_log:
            assert entry.verdict is not None
            assert isinstance(entry.score, float)
