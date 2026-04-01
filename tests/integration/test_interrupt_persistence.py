"""
Integration tests for interrupt persistence and resume.
Requirement IDs: NFR-5, NFR-8
Test Case IDs: TC-NFR-005-01, TC-NFR-008-01
"""

import pytest

from app.models.state_models import (
    InputModality,
    InterruptPayload,
    NormalizedGoal,
    RunState,
    RunStatus,
)
from app.orchestrator.run_manager import RunManager, RunStore
from app.orchestrator.runtime_executor import InterruptManager, RuntimeExecutor


@pytest.mark.integration
class TestInterruptPersistence:

    def test_NFR_008_interrupt_survives_simulated_restart(self):
        """
        Automation ID: AT-NFR-008-INT-01
        Description: Interrupted run can resume after simulated service restart.
        """
        # Phase 1: Create and interrupt run
        store = RunStore()
        manager = RunManager(store)

        run = manager.create_run(
            update_id=500,
            user_id="user-1",
            chat_id="12345",
            input_modality=InputModality.TEXT,
            raw_input="test task",
        )
        run.execution_status = RunStatus.INTERRUPTED
        run.interrupt_payload = InterruptPayload(
            question="Confirm?",
            response_type="choice",
            choices=["Yes", "No"],
            affected_state_fields=["confirmed"],
        )
        run.normalized_goal = NormalizedGoal(goal="test")
        store.save(run)

        # Phase 2: Simulate restart - create new manager using same store
        new_manager = RunManager(store)
        recovered = new_manager.store.get(run.run_id)

        assert recovered is not None
        assert recovered.execution_status == RunStatus.INTERRUPTED
        assert recovered.interrupt_payload is not None
        assert recovered.interrupt_payload.question == "Confirm?"
        assert recovered.thread_id == run.thread_id

    @pytest.mark.asyncio
    async def test_NFR_008_resume_after_recovery(self):
        """
        Description: Run can be resumed after state recovery.
        """
        # Create interrupted state
        run = RunState(
            run_id="recovered-run",
            user_id="user-1",
            chat_id="12345",
            thread_id="thread-12345-500",
            input_modality=InputModality.TEXT,
            execution_status=RunStatus.INTERRUPTED,
            interrupt_payload=InterruptPayload(question="Continue?"),
            normalized_goal=NormalizedGoal(goal="recovered task"),
        )

        executor = RuntimeExecutor()
        result = await executor.resume(run, "Yes, continue")

        assert result.execution_status == RunStatus.EXECUTING
        assert result.thread_id == "thread-12345-500"

    def test_NFR_005_thread_preserved_across_interrupt(self):
        """
        Automation ID: AT-NFR-005-INT-01
        Description: Thread ID is preserved throughout interrupt/resume cycle.
        """
        store = RunStore()
        manager = RunManager(store)

        run = manager.create_run(
            update_id=600,
            user_id="user-1",
            chat_id="12345",
            input_modality=InputModality.TEXT,
            raw_input="test",
        )
        original_thread = run.thread_id

        # Interrupt
        run.execution_status = RunStatus.INTERRUPTED
        store.save(run)

        # Recover
        recovered = store.get(run.run_id)
        assert recovered.thread_id == original_thread

        # Simulate resume
        recovered.execution_status = RunStatus.EXECUTING
        store.save(recovered)

        final = store.get(run.run_id)
        assert final.thread_id == original_thread
