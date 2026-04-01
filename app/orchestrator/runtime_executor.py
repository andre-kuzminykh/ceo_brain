"""
Execution Runtime Service: runs LangGraph workflows with interrupt support.
"""

from __future__ import annotations

from typing import Any

from app.models.state_models import (
    ActionType,
    AtomicAction,
    CriticResult,
    CriticVerdict,
    InterruptPayload,
    RunState,
    RunStatus,
)
from app.orchestrator.critic import StepCritic


class RuntimeExecutor:
    """Executes atomic actions with per-step critic validation."""

    def __init__(
        self,
        step_critic: StepCritic | None = None,
        tool_executor=None,
        llm_executor=None,
        code_executor=None,
    ):
        self.step_critic = step_critic or StepCritic()
        self.tool_executor = tool_executor
        self.llm_executor = llm_executor
        self.code_executor = code_executor
        self.max_retries = 2

    async def execute_actions(
        self, run: RunState, actions: list[AtomicAction]
    ) -> RunState:
        """Execute a list of atomic actions with critic validation."""
        run.execution_status = RunStatus.EXECUTING

        for action in actions:
            run.current_node = action.action_id

            if action.action_type == ActionType.USER_INPUT:
                # Create interrupt
                run.interrupt_payload = InterruptPayload(
                    question=action.tool_params.get("question", action.description),
                    response_type=action.tool_params.get("response_type", "text"),
                    choices=action.tool_params.get("choices", []),
                )
                run.execution_status = RunStatus.INTERRUPTED
                return run

            # Execute with retry loop
            result = None
            for attempt in range(self.max_retries + 1):
                result = await self._execute_single(action)

                # Critic check
                critic_result = await self.step_critic.evaluate(
                    action_description=action.description,
                    expected_schema=None,
                    actual_output=result,
                    goal_context=run.normalized_goal.goal if run.normalized_goal else "",
                )
                run.critic_log.append(critic_result)

                if critic_result.verdict == CriticVerdict.PASS:
                    break
                elif critic_result.verdict == CriticVerdict.ESCALATE:
                    run.execution_status = RunStatus.ESCALATED
                    return run
                # RETRY or REPAIR: loop continues

        run.execution_status = RunStatus.COMPLETED
        return run

    async def resume(self, run: RunState, user_response: str) -> RunState:
        """Resume execution after user interrupt."""
        if run.execution_status != RunStatus.INTERRUPTED:
            raise ValueError(f"Cannot resume run in status {run.execution_status}")

        run.interrupt_payload = None
        run.execution_status = RunStatus.EXECUTING
        return run

    async def _execute_single(self, action: AtomicAction) -> Any:
        if action.action_type == ActionType.LLM:
            if self.llm_executor:
                return await self.llm_executor(action)
            return {"result": f"LLM output for: {action.description}"}

        elif action.action_type == ActionType.TOOL:
            if self.tool_executor:
                return await self.tool_executor(action)
            return {"result": f"Tool output for: {action.tool_name}"}

        elif action.action_type == ActionType.CODE:
            if self.code_executor:
                return await self.code_executor(action)
            return {"result": "code execution result"}

        return None


class InterruptManager:
    """Manages human-in-the-loop interrupts."""

    def __init__(self):
        self._pending: dict[str, InterruptPayload] = {}

    def create_interrupt(self, run_id: str, payload: InterruptPayload):
        self._pending[run_id] = payload

    def get_pending(self, run_id: str) -> InterruptPayload | None:
        return self._pending.get(run_id)

    def resolve(self, run_id: str, response: str, response_type: str = "text") -> dict:
        """Validate and resolve interrupt."""
        payload = self._pending.get(run_id)
        if not payload:
            raise ValueError(f"No pending interrupt for run {run_id}")

        # Validate response
        if payload.response_type == "choice" and payload.choices:
            if response not in payload.choices:
                raise ValueError(
                    f"Invalid choice '{response}'. Valid choices: {payload.choices}"
                )

        if payload.response_type == "text" and not response.strip():
            raise ValueError("Text response cannot be empty")

        del self._pending[run_id]

        return {
            "field": payload.affected_state_fields[0] if payload.affected_state_fields else "user_response",
            "value": response,
        }
