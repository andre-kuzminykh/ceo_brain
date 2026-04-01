"""
Planner & Decomposer: builds plans and decomposes to atomic actions.
"""

from __future__ import annotations

from typing import Any

from app.models.state_models import (
    ActionType,
    AtomicAction,
    ExecutionMode,
    InterruptPayload,
    NormalizedGoal,
    Plan,
    PlanStep,
    RunState,
    RunStatus,
)


class GoalNormalizer:
    """Normalizes raw transcript into structured goal."""

    async def normalize(self, transcript: str, llm_fn=None) -> NormalizedGoal:
        if not transcript or not transcript.strip():
            return NormalizedGoal(
                goal="",
                deliverable="",
                constraints=[],
                ambiguities=["Empty input - unable to determine user intent"],
            )

        # In production, this calls LLM. For now, rule-based extraction.
        goal = transcript.strip()
        deliverable = ""
        constraints = []
        ambiguities = []

        lower = goal.lower()

        # Extract deliverable hints
        if any(kw in lower for kw in ["report", "отчёт", "отчет", "document", "документ"]):
            deliverable = "report"
        elif any(kw in lower for kw in ["summary", "резюме"]):
            deliverable = "summary"

        # Extract constraint hints (geography, time, etc.)
        # Simple heuristic - in production this is LLM-based
        if len(goal.split()) < 4:
            ambiguities.append("Goal is too vague to determine specific intent")

        return NormalizedGoal(
            goal=goal,
            deliverable=deliverable,
            constraints=constraints,
            ambiguities=ambiguities,
        )


class Planner:
    """Builds execution plan from normalized goal."""

    def create_plan(
        self,
        normalized_goal: NormalizedGoal,
        available_capabilities: list[str] | None = None,
    ) -> Plan:
        # If there are ambiguities, return clarifications
        if normalized_goal.ambiguities:
            return Plan(
                execution_mode=ExecutionMode.EXECUTE_TASK,
                steps=[],
                required_tools=[],
                clarifications=normalized_goal.ambiguities,
            )

        # Build basic plan structure
        steps = self._build_steps(normalized_goal)
        required_tools = self._identify_required_tools(normalized_goal)

        return Plan(
            execution_mode=ExecutionMode.EXECUTE_TASK,
            steps=steps,
            required_tools=required_tools,
            clarifications=[],
        )

    def should_clarify(self, plan: Plan) -> bool:
        return len(plan.clarifications) > 0

    def _build_steps(self, goal: NormalizedGoal) -> list[PlanStep]:
        # In production this is LLM-driven
        steps = [
            PlanStep(
                description="Analyze and understand the goal",
                success_criteria="Goal is fully understood with clear deliverable",
            ),
            PlanStep(
                description="Execute core task",
                success_criteria="Task completed with all required outputs",
            ),
        ]

        if goal.deliverable:
            steps.append(
                PlanStep(
                    description=f"Create {goal.deliverable} artifact",
                    success_criteria=f"{goal.deliverable} created and validated",
                )
            )
            steps.append(
                PlanStep(
                    description="Deliver result to user",
                    success_criteria="User received the deliverable",
                )
            )

        return steps

    def _identify_required_tools(self, goal: NormalizedGoal) -> list[str]:
        tools = []
        lower = goal.goal.lower()
        if any(kw in lower for kw in ["search", "research", "find", "рынок", "market"]):
            tools.append("web_search")
        if any(kw in lower for kw in ["google doc", "google docs", "гугл док"]):
            tools.append("google_docs_write")
        return tools


class Decomposer:
    """Decomposes plan steps into atomic actions."""

    def decompose(self, plan: Plan) -> list[AtomicAction]:
        actions = []
        for step in plan.steps:
            step_actions = self._decompose_step(step)
            actions.extend(step_actions)
        return actions

    def _decompose_step(self, step: PlanStep) -> list[AtomicAction]:
        lower = step.description.lower()

        if "analyze" in lower or "understand" in lower:
            return [
                AtomicAction(
                    action_type=ActionType.LLM,
                    description=step.description,
                    success_criteria=step.success_criteria,
                )
            ]
        elif "search" in lower or "retrieve" in lower or "research" in lower:
            return [
                AtomicAction(
                    action_type=ActionType.TOOL,
                    description=step.description,
                    tool_name="web_search",
                    success_criteria=step.success_criteria,
                )
            ]
        elif "create" in lower or "write" in lower or "generate" in lower:
            return [
                AtomicAction(
                    action_type=ActionType.LLM,
                    description=f"Generate content for: {step.description}",
                    success_criteria=step.success_criteria,
                )
            ]
        elif "deliver" in lower or "send" in lower:
            return [
                AtomicAction(
                    action_type=ActionType.TOOL,
                    description=step.description,
                    tool_name="google_docs_write",
                    success_criteria=step.success_criteria,
                )
            ]
        elif "confirm" in lower or "ask" in lower or "clarif" in lower:
            return [
                AtomicAction(
                    action_type=ActionType.USER_INPUT,
                    description=step.description,
                    success_criteria=step.success_criteria,
                )
            ]
        else:
            return [
                AtomicAction(
                    action_type=ActionType.LLM,
                    description=step.description,
                    success_criteria=step.success_criteria,
                )
            ]

    def create_clarification_action(
        self, question: str, choices: list[str] | None = None
    ) -> AtomicAction:
        return AtomicAction(
            action_type=ActionType.USER_INPUT,
            description=f"Ask user: {question}",
            tool_name="request_user_input",
            tool_params={
                "question": question,
                "response_type": "choice" if choices else "text",
                "choices": choices or [],
            },
            success_criteria="User provides valid response",
        )
