"""
Tool Registry & Capability Retrieval Service.
"""

from __future__ import annotations

from app.models.state_models import AtomicAction, ActionType, ToolBinding, ToolDefinition


class ToolRegistry:
    """Manages available tools and matches them to actions."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self._tools[tool.tool_name] = tool

    def get(self, tool_name: str) -> ToolDefinition | None:
        return self._tools.get(tool_name)

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def list_by_category(self, category: str) -> list[ToolDefinition]:
        return [t for t in self._tools.values() if t.category == category]

    def retrieve_tools(
        self,
        actions: list[AtomicAction],
        user_scopes: list[str] | None = None,
    ) -> tuple[list[ToolBinding], list[str], list[str]]:
        """
        Match actions to tools.
        Returns: (bindings, missing_scopes, warnings)
        """
        bindings = []
        missing_scopes = []
        warnings = []
        user_scopes = user_scopes or []

        for action in actions:
            if action.action_type != ActionType.TOOL:
                continue

            if not action.tool_name:
                warnings.append(
                    f"Action '{action.description}' has type=tool but no tool_name"
                )
                continue

            tool = self._tools.get(action.tool_name)
            if not tool:
                # Try to find fallback
                fallback = self._find_fallback(action)
                if fallback:
                    warnings.append(
                        f"Tool '{action.tool_name}' not found, using fallback '{fallback.tool_name}'"
                    )
                    bindings.append(
                        ToolBinding(
                            action_id=action.action_id,
                            tool_name=fallback.tool_name,
                            params=action.tool_params,
                            fallback_tool=action.tool_name,
                        )
                    )
                else:
                    warnings.append(
                        f"Tool '{action.tool_name}' not found, no fallback available. Re-plan needed."
                    )
                continue

            # Check scopes
            for scope in tool.required_scopes:
                if scope not in user_scopes:
                    missing_scopes.append(scope)

            bindings.append(
                ToolBinding(
                    action_id=action.action_id,
                    tool_name=tool.tool_name,
                    params=action.tool_params,
                )
            )

        return bindings, missing_scopes, warnings

    def _find_fallback(self, action: AtomicAction) -> ToolDefinition | None:
        """Find alternative tool with similar capability."""
        if not action.tool_name:
            return None
        # Simple heuristic: look for tools in same category
        for tool in self._tools.values():
            if tool.tool_name != action.tool_name:
                # Check if description overlap suggests capability match
                action_words = set(action.description.lower().split())
                tool_words = set(tool.description.lower().split())
                if len(action_words & tool_words) >= 2:
                    return tool
        return None


def create_default_registry() -> ToolRegistry:
    """Create registry with default tool definitions."""
    registry = ToolRegistry()

    registry.register(ToolDefinition(
        tool_name="web_search",
        category="retrieve",
        description="Search the web for information",
        input_schema={"query": "string"},
        output_schema={"results": "list[dict]"},
    ))

    registry.register(ToolDefinition(
        tool_name="url_reader",
        category="retrieve",
        description="Read content from a URL",
        input_schema={"url": "string"},
        output_schema={"content": "string"},
    ))

    registry.register(ToolDefinition(
        tool_name="google_docs_write",
        category="execution",
        description="Write content to Google Docs",
        input_schema={"title": "string", "content": "string"},
        output_schema={"doc_url": "string"},
        required_scopes=["google_docs_write"],
    ))

    registry.register(ToolDefinition(
        tool_name="request_user_input",
        category="human",
        description="Request input from the user via Telegram",
        input_schema={"question": "string", "response_type": "string", "choices": "list[string]"},
        output_schema={"response": "string"},
    ))

    registry.register(ToolDefinition(
        tool_name="code_exec",
        category="execution",
        description="Execute Python code in sandbox",
        input_schema={"code": "string"},
        output_schema={"result": "any", "stdout": "string", "stderr": "string"},
    ))

    return registry
