"""
Shared test fixtures for the Voice-first Telegram LangGraph Agent system.
"""

import pytest

from app.models.state_models import (
    ActionType,
    AtomicAction,
    CriticResult,
    CriticVerdict,
    ExecutionMode,
    InputModality,
    InterruptPayload,
    NormalizedGoal,
    Plan,
    PlanStep,
    RunState,
    RunStatus,
    ToolBinding,
    ToolDefinition,
)
from app.orchestrator.critic import BuildCritic, RepairService, StepCritic
from app.orchestrator.planner import Decomposer, GoalNormalizer, Planner
from app.orchestrator.run_manager import RunManager, RunStore
from app.orchestrator.tool_registry import ToolRegistry, create_default_registry
from app.orchestrator.artifact_service import ArtifactService
from app.orchestrator.runtime_executor import InterruptManager, RuntimeExecutor
from app.telegram.bot import TelegramGateway, TelegramUpdate


# ---- Telegram fixtures ----

@pytest.fixture
def telegram_gateway():
    sent = []

    async def capture_send(msg):
        sent.append(msg)

    gw = TelegramGateway(bot_token="test-token", send_fn=capture_send)
    gw._captured = sent
    return gw


@pytest.fixture
def voice_update_raw():
    return {
        "update_id": 100,
        "message": {
            "message_id": 1,
            "chat": {"id": 12345},
            "voice": {"file_id": "voice_file_abc", "duration": 5},
        },
    }


@pytest.fixture
def text_update_raw():
    return {
        "update_id": 101,
        "message": {
            "message_id": 2,
            "chat": {"id": 12345},
            "text": "Make a report on EV market in Saudi Arabia and save to Google Docs",
        },
    }


@pytest.fixture
def callback_update_raw():
    return {
        "update_id": 102,
        "callback_query": {
            "id": "cb_1",
            "message": {"message_id": 3, "chat": {"id": 12345}},
            "data": "Google Docs",
        },
    }


@pytest.fixture
def sticker_update_raw():
    return {
        "update_id": 103,
        "message": {
            "message_id": 4,
            "chat": {"id": 12345},
            "sticker": {"file_id": "sticker_abc"},
        },
    }


# ---- Run Manager fixtures ----

@pytest.fixture
def run_store():
    return RunStore()


@pytest.fixture
def run_manager(run_store):
    return RunManager(run_store)


# ---- Planner fixtures ----

@pytest.fixture
def goal_normalizer():
    return GoalNormalizer()


@pytest.fixture
def planner():
    return Planner()


@pytest.fixture
def decomposer():
    return Decomposer()


@pytest.fixture
def clear_goal():
    return NormalizedGoal(
        goal="Research EV market in Saudi Arabia and create a report",
        deliverable="report",
        constraints=["Focus on Saudi Arabia"],
        ambiguities=[],
    )


@pytest.fixture
def ambiguous_goal():
    return NormalizedGoal(
        goal="Do something with the data",
        deliverable="",
        constraints=[],
        ambiguities=["Goal is too vague to determine specific intent"],
    )


# ---- Tool Registry fixtures ----

@pytest.fixture
def tool_registry():
    return create_default_registry()


@pytest.fixture
def empty_registry():
    return ToolRegistry()


# ---- Critic fixtures ----

@pytest.fixture
def step_critic():
    return StepCritic()


@pytest.fixture
def build_critic():
    return BuildCritic()


@pytest.fixture
def repair_service():
    return RepairService()


# ---- Runtime fixtures ----

@pytest.fixture
def runtime_executor():
    return RuntimeExecutor()


@pytest.fixture
def interrupt_manager():
    return InterruptManager()


# ---- Artifact fixtures ----

@pytest.fixture
def artifact_service():
    async def mock_docs_writer(content):
        return "https://docs.google.com/document/d/mock-id/edit"

    return ArtifactService(google_docs_writer=mock_docs_writer)


# ---- Sample data fixtures ----

@pytest.fixture
def sample_run():
    return RunState(
        run_id="run-test-001",
        user_id="user-1",
        chat_id="12345",
        thread_id="thread-12345-100",
        input_modality=InputModality.VOICE,
        raw_input="voice_file_abc",
        execution_status=RunStatus.RECEIVED,
    )


@pytest.fixture
def sample_actions():
    return [
        AtomicAction(
            action_id="act-1",
            action_type=ActionType.LLM,
            description="Analyze the goal",
            success_criteria="Goal analyzed",
        ),
        AtomicAction(
            action_id="act-2",
            action_type=ActionType.TOOL,
            description="Search for market data",
            tool_name="web_search",
            tool_params={"query": "EV market Saudi Arabia"},
            success_criteria="Search results obtained",
        ),
        AtomicAction(
            action_id="act-3",
            action_type=ActionType.LLM,
            description="Generate report",
            success_criteria="Report generated",
        ),
    ]


@pytest.fixture
def valid_generated_files():
    return {
        "state.py": "from typing import TypedDict\n\nclass State(TypedDict):\n    data: str\n",
        "nodes.py": "def process(state):\n    return {'data': 'processed'}\n",
        "graph.py": "from state import State\nfrom nodes import process\n",
        "run.py": "print('running')\n",
    }


@pytest.fixture
def invalid_generated_files():
    return {
        "state.py": "from typing import TypedDict\n\nclass State(TypedDict):\n    data: str\n",
        "nodes.py": "def process(state)\n    return {'data': 'processed'}\n",  # Missing colon
        "graph.py": "from state import State\n",
        "run.py": "print('running')\n",
    }


@pytest.fixture
def interrupt_payload_choice():
    return InterruptPayload(
        question="Which format do you prefer?",
        response_type="choice",
        choices=["PDF", "Google Docs", "Email"],
        affected_state_fields=["delivery_format"],
    )


@pytest.fixture
def interrupt_payload_text():
    return InterruptPayload(
        question="What specific aspects should the report cover?",
        response_type="text",
        affected_state_fields=["report_focus"],
    )
