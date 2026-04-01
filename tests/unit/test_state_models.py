"""
Unit tests for state models.
Covers: FR-3, FR-5, FR-6, FR-10, NFR-4, NFR-6, NFR-11
"""

import pytest

from app.models.state_models import (
    ActionType,
    AtomicAction,
    CriticResult,
    CriticVerdict,
    ErrorClass,
    ExecutionMode,
    InputModality,
    InterruptPayload,
    NormalizedGoal,
    Plan,
    PlanStep,
    RepairAttempt,
    RunState,
    RunStatus,
    ToolBinding,
    ToolDefinition,
    Artifact,
)


@pytest.mark.unit
class TestNormalizedGoal:
    """
    Requirement ID: FR-3
    Test Case IDs: TC-FR-003-01, TC-FR-003-02, TC-FR-003-03
    """

    def test_FR_003_complete_goal_serialization(self):
        """
        Automation ID: AT-FR-003-UNIT-01
        Description: Complete goal with all fields serializes correctly.
        """
        goal = NormalizedGoal(
            goal="Research EV market in Saudi Arabia",
            deliverable="report",
            constraints=["Focus on Saudi Arabia", "Include 2024 data"],
            ambiguities=[],
        )
        assert goal.goal == "Research EV market in Saudi Arabia"
        assert goal.deliverable == "report"
        assert len(goal.constraints) == 2
        assert len(goal.ambiguities) == 0

    def test_FR_003_ambiguous_goal_has_ambiguities(self):
        """
        Automation ID: AT-FR-003-UNIT-02
        Description: Vague goal produces non-empty ambiguities list.
        """
        goal = NormalizedGoal(
            goal="Do something",
            deliverable="",
            constraints=[],
            ambiguities=["Goal is too vague"],
        )
        assert goal.ambiguities
        assert goal.deliverable == ""

    def test_FR_003_empty_goal_defaults(self):
        """
        Automation ID: AT-FR-003-UNIT-03
        Description: Empty goal has correct defaults.
        """
        goal = NormalizedGoal(goal="")
        assert goal.goal == ""
        assert goal.deliverable == ""
        assert goal.constraints == []
        assert goal.ambiguities == []


@pytest.mark.unit
class TestAtomicAction:
    """
    Requirement ID: FR-6
    Test Case IDs: TC-FR-006-01, TC-FR-006-02
    """

    def test_FR_006_action_types_are_valid_enum(self):
        """
        Automation ID: AT-FR-006-UNIT-02
        Description: All action types are valid enum members.
        """
        for at in ActionType:
            assert at.value in {"llm", "tool", "code", "user_input"}

    def test_FR_006_llm_action_creation(self):
        """
        Automation ID: AT-FR-006-UNIT-01 (partial)
        Description: LLM action is correctly constructed.
        """
        action = AtomicAction(
            action_type=ActionType.LLM,
            description="Analyze market trends",
            success_criteria="Key trends identified",
        )
        assert action.action_type == ActionType.LLM
        assert action.tool_name is None
        assert action.action_id  # UUID auto-generated

    def test_FR_006_tool_action_has_tool_name(self):
        """
        Automation ID: AT-FR-006-UNIT-01 (partial)
        Description: Tool action has tool_name populated.
        """
        action = AtomicAction(
            action_type=ActionType.TOOL,
            description="Search web for data",
            tool_name="web_search",
            tool_params={"query": "EV market"},
        )
        assert action.action_type == ActionType.TOOL
        assert action.tool_name == "web_search"
        assert action.tool_params["query"] == "EV market"

    def test_FR_006_user_input_action(self):
        """
        Automation ID: AT-FR-005-UNIT-01 (partial)
        Description: User input action type for clarifications.
        """
        action = AtomicAction(
            action_type=ActionType.USER_INPUT,
            description="Ask user for format preference",
            tool_name="request_user_input",
            tool_params={
                "question": "Which format?",
                "response_type": "choice",
                "choices": ["PDF", "Google Docs"],
            },
        )
        assert action.action_type == ActionType.USER_INPUT
        assert action.tool_name == "request_user_input"


@pytest.mark.unit
class TestInterruptPayload:
    """
    Requirement ID: FR-5, NFR-4
    Test Case IDs: TC-FR-005-01, TC-NFR-004-01
    """

    def test_FR_005_interrupt_as_user_input_contract(self):
        """
        Automation ID: AT-FR-005-UNIT-01
        Description: InterruptPayload follows user_input contract.
        """
        payload = InterruptPayload(
            tool_name="request_user_input",
            response_type="choice",
            question="Which format?",
            choices=["PDF", "Google Docs", "Email"],
            affected_state_fields=["delivery_format"],
        )
        assert payload.tool_name == "request_user_input"
        assert payload.response_type == "choice"
        assert len(payload.choices) == 3

    def test_NFR_004_supports_text_response_type(self):
        """
        Automation ID: AT-NFR-004-UNIT-01 (partial)
        Description: InterruptPayload supports text response type.
        """
        payload = InterruptPayload(
            question="What should the focus be?",
            response_type="text",
        )
        assert payload.response_type == "text"
        assert payload.choices == []

    def test_NFR_004_supports_choice_response_type(self):
        """
        Automation ID: AT-NFR-004-UNIT-01 (partial)
        Description: InterruptPayload supports choice response type.
        """
        payload = InterruptPayload(
            question="Pick one",
            response_type="choice",
            choices=["A", "B"],
        )
        assert payload.response_type == "choice"
        assert len(payload.choices) == 2


@pytest.mark.unit
class TestRunState:
    """
    Requirement IDs: FR-4, NFR-2
    """

    def test_run_state_defaults(self):
        """RunState initializes with correct defaults."""
        run = RunState()
        assert run.run_id
        assert run.execution_status == RunStatus.RECEIVED
        assert run.critic_log == []
        assert run.repair_attempts == []
        assert run.artifacts == []

    def test_run_status_transitions(self):
        """All required status values exist in enum."""
        required = {
            "received", "transcribed", "understood", "planned",
            "waiting_for_user", "tools_bound", "graph_built",
            "executing", "interrupted", "artifact_ready",
            "delivered", "completed", "failed", "escalated",
        }
        actual = {s.value for s in RunStatus}
        assert required.issubset(actual)


@pytest.mark.unit
class TestCriticResult:
    """
    Requirement ID: FR-11, NFR-11
    Test Case ID: TC-NFR-011-01
    """

    def test_critic_verdicts_exist(self):
        """All verdict types exist."""
        assert CriticVerdict.PASS.value == "pass"
        assert CriticVerdict.RETRY.value == "retry"
        assert CriticVerdict.REPAIR.value == "repair"
        assert CriticVerdict.ESCALATE.value == "escalate"

    def test_NFR_011_repair_attempt_has_required_fields(self):
        """
        Automation ID: AT-NFR-011-UNIT-01
        Description: RepairAttempt has all required tracing fields.
        """
        attempt = RepairAttempt(
            attempt_number=1,
            error_class=ErrorClass.CODEGEN_ERROR,
            fix_strategy="Fix syntax errors",
            files_changed=["nodes.py"],
            validation_passed=False,
            traceback="SyntaxError at line 5",
        )
        assert attempt.attempt_number == 1
        assert attempt.error_class == ErrorClass.CODEGEN_ERROR
        assert attempt.fix_strategy
        assert attempt.files_changed
        assert attempt.traceback

    def test_NFR_011_repair_log_ordered(self):
        """
        Automation ID: AT-NFR-011-UNIT-01 (partial)
        Description: Multiple repair attempts maintain order.
        """
        attempts = [
            RepairAttempt(attempt_number=i, error_class=ErrorClass.CODEGEN_ERROR, fix_strategy=f"fix-{i}")
            for i in range(1, 4)
        ]
        assert [a.attempt_number for a in attempts] == [1, 2, 3]


@pytest.mark.unit
class TestNFR6SideEffectsOnlyViaTools:
    """
    Requirement ID: NFR-6
    Test Case ID: TC-NFR-006-01
    """

    def test_NFR_006_llm_action_has_no_tool(self):
        """
        Automation ID: AT-NFR-006-UNIT-01 (partial)
        Description: LLM action type does not carry tool binding.
        """
        action = AtomicAction(
            action_type=ActionType.LLM,
            description="Generate analysis",
        )
        assert action.tool_name is None

    def test_NFR_006_code_action_has_no_external_tool(self):
        """
        Automation ID: AT-NFR-006-UNIT-01 (partial)
        Description: Code action type is for deterministic transformations.
        """
        action = AtomicAction(
            action_type=ActionType.CODE,
            description="Transform data format",
        )
        assert action.tool_name is None

    def test_NFR_006_only_tool_type_has_tool_name(self):
        """
        Automation ID: AT-NFR-006-UNIT-01
        Description: Only tool-type actions carry tool bindings for side effects.
        """
        tool_action = AtomicAction(
            action_type=ActionType.TOOL,
            description="Write to Google Docs",
            tool_name="google_docs_write",
        )
        assert tool_action.tool_name is not None

        for at in [ActionType.LLM, ActionType.CODE]:
            action = AtomicAction(action_type=at, description="test")
            assert action.tool_name is None
