"""
Unit tests for Tool Registry.
Requirement IDs: FR-7
Test Case IDs: TC-FR-007-01, TC-FR-007-02
"""

import pytest

from app.models.state_models import ActionType, AtomicAction, ToolDefinition
from app.orchestrator.tool_registry import ToolRegistry, create_default_registry


@pytest.mark.unit
class TestToolRegistry:

    def test_FR_007_register_and_retrieve_tool(self, empty_registry):
        """Description: Tool can be registered and retrieved by name."""
        tool = ToolDefinition(
            tool_name="test_tool",
            category="retrieve",
            description="A test tool",
        )
        empty_registry.register(tool)
        assert empty_registry.get("test_tool") is not None
        assert empty_registry.get("nonexistent") is None

    def test_FR_007_default_registry_has_core_tools(self, tool_registry):
        """Description: Default registry contains expected tools."""
        assert tool_registry.get("web_search") is not None
        assert tool_registry.get("google_docs_write") is not None
        assert tool_registry.get("request_user_input") is not None
        assert tool_registry.get("code_exec") is not None

    def test_FR_007_retrieve_matches_tools_to_actions(self, tool_registry):
        """
        Automation ID: AT-FR-007-UNIT-01
        Description: Tool retriever matches correct tools by action requirements.
        """
        actions = [
            AtomicAction(
                action_type=ActionType.TOOL,
                description="Search for market data",
                tool_name="web_search",
                tool_params={"query": "EV market"},
            ),
            AtomicAction(
                action_type=ActionType.TOOL,
                description="Write report to Google Docs",
                tool_name="google_docs_write",
            ),
            AtomicAction(
                action_type=ActionType.LLM,
                description="Analyze data",  # Not a tool action, should be skipped
            ),
        ]

        bindings, missing_scopes, warnings = tool_registry.retrieve_tools(
            actions, user_scopes=["google_docs_write"]
        )

        assert len(bindings) == 2
        assert bindings[0].tool_name == "web_search"
        assert bindings[1].tool_name == "google_docs_write"
        assert len(warnings) == 0

    def test_FR_007_missing_scope_detected(self, tool_registry):
        """Description: Missing user scopes are detected."""
        actions = [
            AtomicAction(
                action_type=ActionType.TOOL,
                description="Write to docs",
                tool_name="google_docs_write",
            ),
        ]

        bindings, missing_scopes, warnings = tool_registry.retrieve_tools(
            actions, user_scopes=[]  # No scopes granted
        )

        assert "google_docs_write" in missing_scopes

    def test_FR_007_missing_tool_generates_warning(self, tool_registry):
        """
        Automation ID: AT-FR-007-UNIT-02
        Description: Missing tool triggers warning and fallback attempt.
        """
        actions = [
            AtomicAction(
                action_type=ActionType.TOOL,
                description="Send via Slack",
                tool_name="slack_send",
            ),
        ]

        bindings, missing_scopes, warnings = tool_registry.retrieve_tools(actions)

        assert len(warnings) > 0
        assert any("slack_send" in w for w in warnings)

    def test_FR_007_tool_action_without_name_warned(self, tool_registry):
        """Description: Tool action without tool_name generates warning."""
        actions = [
            AtomicAction(
                action_type=ActionType.TOOL,
                description="Do something external",
            ),
        ]

        bindings, missing_scopes, warnings = tool_registry.retrieve_tools(actions)
        assert len(warnings) > 0

    def test_list_by_category(self, tool_registry):
        """Description: Tools can be filtered by category."""
        retrieve_tools = tool_registry.list_by_category("retrieve")
        assert len(retrieve_tools) >= 1
        assert all(t.category == "retrieve" for t in retrieve_tools)
