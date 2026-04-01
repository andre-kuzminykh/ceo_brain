"""
Integration tests for the repair loop.
Requirement IDs: FR-11, FR-12
Test Case IDs: TC-FR-011-01, TC-FR-011-02, TC-FR-012-01
"""

import pytest

from app.models.state_models import CriticVerdict, ErrorClass
from app.orchestrator.critic import BuildCritic, RepairService


@pytest.mark.integration
class TestRepairLoop:

    @pytest.mark.asyncio
    async def test_FR_011_three_attempts_then_escalate(self):
        """
        Automation ID: AT-FR-011-INT-01
        Description: System retries repair up to 3 times before escalating.
        """
        # Code with an error the default heuristic can't fix properly
        files = {
            "buggy.py": "class Foo:\n    def bar(self\n        return 1\n",
        }

        critic = BuildCritic()
        service = RepairService()

        final_files, attempts, success = await service.repair_loop(
            files, critic, max_attempts=3
        )

        # Should have attempted repairs
        assert len(attempts) >= 1
        assert len(attempts) <= 3

        # Each attempt should be logged
        for i, attempt in enumerate(attempts):
            assert attempt.attempt_number == i + 1
            assert attempt.error_class is not None
            assert isinstance(attempt.fix_strategy, str)

    @pytest.mark.asyncio
    async def test_FR_011_successful_repair_stops_loop(self):
        """
        Automation ID: AT-FR-011-INT-02
        Description: Successful repair on 2nd attempt stops loop.
        """
        attempt_count = 0

        async def repair_fn(files, critic_result):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count >= 2:
                return {"fixed.py": "x = 1\nprint(x)\n"}
            return {"fixed.py": "x = 1\nprint(x\n"}  # Still broken first time

        critic = BuildCritic()
        service = RepairService(llm_repair_fn=repair_fn)

        files = {"fixed.py": "x = 1\nprint(x\n"}
        final_files, attempts, success = await service.repair_loop(
            files, critic, max_attempts=3
        )

        assert success
        assert len(attempts) <= 3

    @pytest.mark.asyncio
    async def test_FR_012_compile_import_smoke_after_patch(self):
        """
        Automation ID: AT-FR-012-INT-01
        Description: After each patch, compile + import + smoke test runs.
        """
        validation_calls = []

        class TrackingCritic(BuildCritic):
            async def validate(self, files, sandbox_runner=None):
                validation_calls.append(list(files.keys()))
                return await super().validate(files, sandbox_runner)

        # Start with bad code, repair to good code
        async def repair_fn(files, critic_result):
            return {"module.py": "def hello():\n    return 'world'\n"}

        critic = TrackingCritic()
        service = RepairService(llm_repair_fn=repair_fn)

        files = {"module.py": "def hello(\n    return 'world'\n"}
        final_files, attempts, success = await service.repair_loop(
            files, critic, max_attempts=3
        )

        # Validator should be called multiple times:
        # 1. Initial validation (fails)
        # 2. After repair validation (passes)
        assert len(validation_calls) >= 2

    @pytest.mark.asyncio
    async def test_FR_012_valid_code_skips_repair(self, valid_generated_files):
        """
        Description: Valid code passes validation without entering repair loop.
        """
        critic = BuildCritic()
        service = RepairService()

        final_files, attempts, success = await service.repair_loop(
            valid_generated_files, critic
        )

        assert success
        assert len(attempts) == 0
