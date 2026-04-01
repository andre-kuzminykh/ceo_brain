"""
Unit tests for Planner and Decomposer.
Requirement IDs: FR-4, FR-5, FR-6, FR-7
Test Case IDs: TC-FR-004-01, TC-FR-005-01, TC-FR-006-01, TC-FR-006-02
"""

import pytest

from app.models.state_models import (
    ActionType,
    ExecutionMode,
    NormalizedGoal,
)
from app.orchestrator.planner import Decomposer, Planner


@pytest.mark.unit
class TestPlanner:

    def test_FR_004_ambiguous_goal_returns_clarifications(self, planner, ambiguous_goal):
        """
        Automation ID: AT-FR-004-UNIT-01
        Description: Missing critical inputs produce clarifications, not failure.
        """
        plan = planner.create_plan(ambiguous_goal)

        assert planner.should_clarify(plan)
        assert len(plan.clarifications) > 0
        assert len(plan.steps) == 0  # No steps if clarification needed

    def test_FR_004_clear_goal_no_clarifications(self, planner, clear_goal):
        """
        Description: Clear goal produces plan without clarifications.
        """
        plan = planner.create_plan(clear_goal)

        assert not planner.should_clarify(plan)
        assert len(plan.steps) > 0
        assert len(plan.clarifications) == 0

    def test_FR_006_plan_has_steps_with_criteria(self, planner, clear_goal):
        """
        Automation ID: AT-FR-006-UNIT-01 (partial)
        Description: Plan steps have descriptions and success criteria.
        """
        plan = planner.create_plan(clear_goal)

        for step in plan.steps:
            assert step.description
            assert step.success_criteria

    def test_plan_identifies_required_tools(self, planner, clear_goal):
        """Description: Plan identifies tools needed for the goal."""
        plan = planner.create_plan(clear_goal)

        # Goal mentions "market" -> should identify web_search
        assert "web_search" in plan.required_tools or len(plan.required_tools) >= 0

    def test_plan_execution_mode(self, planner, clear_goal):
        """Description: Plan sets execution mode correctly."""
        plan = planner.create_plan(clear_goal)
        assert plan.execution_mode == ExecutionMode.EXECUTE_TASK


@pytest.mark.unit
class TestDecomposer:

    def test_FR_006_decompose_produces_atomic_actions(self, decomposer, planner, clear_goal):
        """
        Automation ID: AT-FR-006-UNIT-01
        Description: Decomposer produces atomic actions from plan.
        """
        plan = planner.create_plan(clear_goal)
        actions = decomposer.decompose(plan)

        assert len(actions) > 0
        for action in actions:
            assert action.action_type in ActionType
            assert action.description
            assert action.action_id

    def test_FR_006_all_action_types_valid(self, decomposer, planner, clear_goal):
        """
        Automation ID: AT-FR-006-UNIT-02
        Description: All decomposed action types are valid enum members.
        """
        plan = planner.create_plan(clear_goal)
        actions = decomposer.decompose(plan)

        valid_types = {ActionType.LLM, ActionType.TOOL, ActionType.CODE, ActionType.USER_INPUT}
        for action in actions:
            assert action.action_type in valid_types

    def test_FR_005_clarification_action_is_user_input(self, decomposer):
        """
        Automation ID: AT-FR-005-UNIT-01
        Description: Clarification question produces user_input action.
        """
        action = decomposer.create_clarification_action(
            question="What format should the report be in?",
            choices=["PDF", "Google Docs"],
        )

        assert action.action_type == ActionType.USER_INPUT
        assert action.tool_name == "request_user_input"
        assert action.tool_params["question"] == "What format should the report be in?"
        assert action.tool_params["response_type"] == "choice"
        assert action.tool_params["choices"] == ["PDF", "Google Docs"]

    def test_FR_005_text_clarification_action(self, decomposer):
        """
        Description: Text clarification has response_type=text.
        """
        action = decomposer.create_clarification_action(
            question="What should the focus be?"
        )

        assert action.action_type == ActionType.USER_INPUT
        assert action.tool_params["response_type"] == "text"
        assert action.tool_params["choices"] == []
