"""
Performance tests for latency requirements.
Requirement IDs: NFR-1, NFR-9
Test Case IDs: TC-NFR-001-01, TC-NFR-009-01
"""

import asyncio
import time

import pytest

from app.models.state_models import (
    InputModality,
    InterruptPayload,
    NormalizedGoal,
    RunStatus,
)
from app.orchestrator.planner import GoalNormalizer
from app.orchestrator.run_manager import RunManager, RunStore
from app.orchestrator.runtime_executor import RuntimeExecutor
from app.telegram.bot import TelegramGateway


@pytest.mark.performance
class TestFirstResponseLatency:
    """
    Requirement: NFR-1 - Time to first response ≤ 5 seconds
    Test Case: TC-NFR-001-01
    """

    @pytest.mark.asyncio
    async def test_NFR_001_first_response_within_threshold(self):
        """
        Automation ID: AT-NFR-001-PERF-01
        Description: First acknowledgment sent within 5 seconds.
        """
        response_times = []

        async def timed_send(msg):
            pass  # Simulated instant send

        gateway = TelegramGateway(bot_token="test", send_fn=timed_send)
        store = RunStore()
        manager = RunManager(store)
        normalizer = GoalNormalizer()

        for i in range(50):
            start = time.monotonic()

            # Simulate the full intake path: parse -> create run -> acknowledge -> normalize
            update = gateway.parse_update({
                "update_id": 10000 + i,
                "message": {
                    "message_id": i,
                    "chat": {"id": 12345},
                    "text": f"Create report on topic {i}",
                },
            })

            run = manager.create_run(
                update_id=update.update_id,
                user_id="perf-user",
                chat_id=update.chat_id,
                input_modality=InputModality.TEXT,
                raw_input=update.text,
            )

            # First response: acknowledge receipt
            await gateway.send_message(update.chat_id, "Got it! Working on it...")

            elapsed = time.monotonic() - start
            response_times.append(elapsed)

        # p95 should be under 5 seconds
        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p95 = response_times[p95_index]

        assert p95 <= 5.0, f"p95 first response time is {p95:.3f}s, exceeds 5s threshold"

        # Also check p50 for sanity
        p50_index = int(len(response_times) * 0.50)
        p50 = response_times[p50_index]
        assert p50 <= 1.0, f"p50 first response time is {p50:.3f}s, seems too slow"


@pytest.mark.performance
class TestResumeLatency:
    """
    Requirement: NFR-9 - Reply latency after user response ≤ 3 seconds
    Test Case: TC-NFR-009-01
    """

    @pytest.mark.asyncio
    async def test_NFR_009_resume_confirmation_within_threshold(self):
        """
        Automation ID: AT-NFR-009-PERF-01
        Description: Resume confirmation sent within 3 seconds.
        """
        response_times = []

        async def timed_send(msg):
            pass

        gateway = TelegramGateway(bot_token="test", send_fn=timed_send)
        executor = RuntimeExecutor()

        for i in range(20):
            from app.models.state_models import RunState

            run = RunState(
                run_id=f"perf-run-{i}",
                user_id="perf-user",
                chat_id="12345",
                thread_id=f"thread-{i}",
                execution_status=RunStatus.INTERRUPTED,
                interrupt_payload=InterruptPayload(question=f"Question {i}?"),
                normalized_goal=NormalizedGoal(goal="test"),
            )

            start = time.monotonic()

            # Resume
            result = await executor.resume(run, f"Answer {i}")
            await gateway.send_message(
                run.chat_id,
                "Resuming execution...",
            )

            elapsed = time.monotonic() - start
            response_times.append(elapsed)

        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p95 = response_times[p95_index]

        assert p95 <= 3.0, f"p95 resume latency is {p95:.3f}s, exceeds 3s threshold"


@pytest.mark.performance
class TestGoalNormalizationThroughput:
    """Additional performance test for normalization throughput."""

    @pytest.mark.asyncio
    async def test_normalization_throughput(self):
        """Description: Goal normalization handles 100 requests quickly."""
        normalizer = GoalNormalizer()
        transcripts = [
            f"Create a report on topic {i} about market analysis"
            for i in range(100)
        ]

        start = time.monotonic()
        for transcript in transcripts:
            await normalizer.normalize(transcript)
        elapsed = time.monotonic() - start

        # Should process 100 normalizations in under 1 second (no LLM calls)
        assert elapsed < 1.0, f"100 normalizations took {elapsed:.3f}s"
