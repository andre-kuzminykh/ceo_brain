"""
State models for the Voice-first Telegram LangGraph Agent system.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class InputModality(str, Enum):
    VOICE = "voice"
    TEXT = "text"
    CALLBACK = "callback"


class RunStatus(str, Enum):
    RECEIVED = "received"
    TRANSCRIBED = "transcribed"
    UNDERSTOOD = "understood"
    PLANNED = "planned"
    WAITING_FOR_USER = "waiting_for_user"
    TOOLS_BOUND = "tools_bound"
    GRAPH_BUILT = "graph_built"
    EXECUTING = "executing"
    INTERRUPTED = "interrupted"
    ARTIFACT_READY = "artifact_ready"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class ExecutionMode(str, Enum):
    EXECUTE_TASK = "execute_task"
    AUTHOR_WORKFLOW = "author_workflow"


class ActionType(str, Enum):
    LLM = "llm"
    TOOL = "tool"
    CODE = "code"
    USER_INPUT = "user_input"


class CriticVerdict(str, Enum):
    PASS = "pass"
    RETRY = "retry"
    REPAIR = "repair"
    ESCALATE = "escalate"


class ErrorClass(str, Enum):
    SPEC_ERROR = "spec_error"
    CODEGEN_ERROR = "codegen_error"
    ROUTING_ERROR = "routing_error"
    TOOL_CONTRACT_ERROR = "tool_contract_error"
    RUNTIME_ERROR = "runtime_error"
    INFINITE_LOOP_RISK = "infinite_loop_risk"


class NormalizedGoal(BaseModel):
    goal: str
    deliverable: str = ""
    constraints: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)


class AtomicAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType
    description: str
    tool_name: str | None = None
    tool_params: dict[str, Any] = Field(default_factory=dict)
    success_criteria: str = ""
    depends_on: list[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    actions: list[AtomicAction] = Field(default_factory=list)
    success_criteria: str = ""


class Plan(BaseModel):
    execution_mode: ExecutionMode
    steps: list[PlanStep] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    clarifications: list[str] = Field(default_factory=list)


class InterruptPayload(BaseModel):
    tool_name: str = "request_user_input"
    response_type: str = "text"
    question: str
    choices: list[str] = Field(default_factory=list)
    affected_state_fields: list[str] = Field(default_factory=list)


class CriticResult(BaseModel):
    verdict: CriticVerdict
    issues: list[str] = Field(default_factory=list)
    score: float = 0.0
    root_cause: str = ""
    error_class: ErrorClass | None = None
    fix_strategy: list[str] = Field(default_factory=list)
    files_to_change: list[str] = Field(default_factory=list)
    tests_to_run: list[str] = Field(default_factory=list)


class ToolDefinition(BaseModel):
    tool_name: str
    category: str  # retrieve, execution, human, control
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    required_scopes: list[str] = Field(default_factory=list)


class ToolBinding(BaseModel):
    action_id: str
    tool_name: str
    params: dict[str, Any] = Field(default_factory=dict)
    fallback_tool: str | None = None


class RepairAttempt(BaseModel):
    attempt_number: int
    error_class: ErrorClass
    fix_strategy: str
    files_changed: list[str] = Field(default_factory=list)
    validation_passed: bool = False
    traceback: str = ""


class Artifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type: str  # report, memo, research_pack
    content: dict[str, Any] = Field(default_factory=dict)
    artifact_url: str = ""
    delivery_status: str = "pending"


class RunState(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    chat_id: str = ""
    thread_id: str = ""
    input_modality: InputModality = InputModality.TEXT
    raw_input: str = ""
    transcript: str = ""
    normalized_goal: NormalizedGoal | None = None
    clarifications: list[str] = Field(default_factory=list)
    plan: Plan | None = None
    atomic_actions: list[AtomicAction] = Field(default_factory=list)
    selected_tools: list[str] = Field(default_factory=list)
    tool_bindings: list[ToolBinding] = Field(default_factory=list)
    workflow_spec: str = ""
    generated_files: dict[str, str] = Field(default_factory=dict)
    execution_status: RunStatus = RunStatus.RECEIVED
    current_node: str = ""
    interrupt_payload: InterruptPayload | None = None
    critic_log: list[CriticResult] = Field(default_factory=list)
    repair_attempts: list[RepairAttempt] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    final_summary: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
