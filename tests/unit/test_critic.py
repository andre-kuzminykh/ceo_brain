"""
Unit tests for Critic and Repair services.
Requirement IDs: FR-8, FR-11, FR-12, NFR-11
Test Case IDs: TC-FR-008-01, TC-FR-011-01, TC-FR-011-02, TC-FR-012-01, TC-NFR-011-01
"""

import pytest

from app.models.state_models import CriticVerdict, ErrorClass
from app.orchestrator.critic import BuildCritic, RepairService, StepCritic


@pytest.mark.unit
class TestStepCritic:

    @pytest.mark.asyncio
    async def test_valid_output_passes(self, step_critic):
        """Description: Valid non-empty output gets pass verdict."""
        result = await step_critic.evaluate(
            action_description="Generate analysis",
            expected_schema=None,
            actual_output={"analysis": "Market is growing"},
        )
        assert result.verdict == CriticVerdict.PASS
        assert result.score >= 0.8

    @pytest.mark.asyncio
    async def test_none_output_retries(self, step_critic):
        """Description: None output triggers retry."""
        result = await step_critic.evaluate(
            action_description="Search",
            expected_schema=None,
            actual_output=None,
        )
        assert result.verdict == CriticVerdict.RETRY
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_empty_string_output_low_score(self, step_critic):
        """Description: Empty string output gets low score."""
        result = await step_critic.evaluate(
            action_description="Generate report",
            expected_schema=None,
            actual_output="",
        )
        assert result.score < 0.8

    @pytest.mark.asyncio
    async def test_empty_dict_output_low_score(self, step_critic):
        """Description: Empty dict output gets low score."""
        result = await step_critic.evaluate(
            action_description="Retrieve data",
            expected_schema=None,
            actual_output={},
        )
        assert result.score < 0.8

    @pytest.mark.asyncio
    async def test_schema_check_missing_fields(self, step_critic):
        """Description: Missing required schema fields reduce score."""
        result = await step_critic.evaluate(
            action_description="Get results",
            expected_schema={"results": "list", "count": "int"},
            actual_output={"results": [1, 2]},  # Missing "count"
        )
        assert len(result.issues) > 0
        assert any("count" in issue for issue in result.issues)

    @pytest.mark.asyncio
    async def test_FR_008_critic_pass_verdict(self, step_critic):
        """
        Automation ID: AT-FR-008-INT-01 (unit portion)
        Description: Good output gets PASS verdict allowing delivery.
        """
        result = await step_critic.evaluate(
            action_description="Final report",
            expected_schema=None,
            actual_output={"title": "Report", "content": "Full analysis..."},
        )
        assert result.verdict == CriticVerdict.PASS


@pytest.mark.unit
class TestBuildCritic:

    @pytest.mark.asyncio
    async def test_valid_files_pass(self, build_critic, valid_generated_files):
        """Description: Syntactically valid files pass build critic."""
        result = await build_critic.validate(valid_generated_files)
        assert result.verdict == CriticVerdict.PASS
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_syntax_error_detected(self, build_critic, invalid_generated_files):
        """Description: Syntax errors are detected as REPAIR verdict."""
        result = await build_critic.validate(invalid_generated_files)
        assert result.verdict == CriticVerdict.REPAIR
        assert result.error_class == ErrorClass.CODEGEN_ERROR
        assert len(result.issues) > 0
        assert any("SyntaxError" in i for i in result.issues)

    @pytest.mark.asyncio
    async def test_FR_012_validation_stages(self, build_critic, valid_generated_files):
        """
        Automation ID: AT-FR-012-INT-01 (unit portion)
        Description: Both compile and import checks run.
        """
        result = await build_critic.validate(valid_generated_files)
        # Valid files should pass both compile and import
        assert result.verdict == CriticVerdict.PASS

    @pytest.mark.asyncio
    async def test_bad_import_detected(self, build_critic):
        """Description: Bad imports are detected."""
        files = {
            "test.py": "import nonexistent_module\nprint('hello')\n",
        }
        result = await build_critic.validate(files)
        assert result.verdict == CriticVerdict.REPAIR
        assert any("import" in i.lower() for i in result.issues)


@pytest.mark.unit
class TestRepairService:

    @pytest.mark.asyncio
    async def test_FR_011_repair_loop_max_attempts(self, repair_service, build_critic):
        """
        Automation ID: AT-FR-011-INT-01 (unit portion)
        Description: Repair loop makes up to 3 attempts.
        """
        # Files with a persistent error that heuristic repair can't fully fix
        files = {
            "broken.py": "def f(\n    pass\n",  # Persistent syntax error
        }

        final_files, attempts, success = await repair_service.repair_loop(
            files, build_critic, max_attempts=3
        )

        assert len(attempts) >= 1
        assert len(attempts) <= 3
        for attempt in attempts:
            assert attempt.attempt_number >= 1
            assert attempt.error_class is not None
            assert attempt.fix_strategy

    @pytest.mark.asyncio
    async def test_FR_011_successful_repair_stops_loop(self, build_critic):
        """
        Automation ID: AT-FR-011-INT-02 (unit portion)
        Description: Successful repair stops the retry loop.
        """
        call_count = 0

        async def mock_repair(files, critic_result):
            nonlocal call_count
            call_count += 1
            # Fix the syntax error on second attempt
            return {
                "fixed.py": "def f():\n    pass\n",
            }

        service = RepairService(llm_repair_fn=mock_repair)
        files = {
            "fixed.py": "def f(\n    pass\n",
        }

        final_files, attempts, success = await service.repair_loop(
            files, build_critic, max_attempts=3
        )

        assert success
        assert call_count <= 2  # Should stop after successful repair

    @pytest.mark.asyncio
    async def test_NFR_011_repair_log_complete(self, repair_service, build_critic):
        """
        Automation ID: AT-NFR-011-UNIT-01
        Description: Repair log has all required fields.
        """
        files = {"bad.py": "import nonexistent_module\n"}
        final_files, attempts, success = await repair_service.repair_loop(
            files, build_critic, max_attempts=2
        )

        for attempt in attempts:
            assert isinstance(attempt.attempt_number, int)
            assert attempt.error_class is not None
            assert isinstance(attempt.fix_strategy, str)
            assert isinstance(attempt.files_changed, list)
            assert isinstance(attempt.validation_passed, bool)
            assert isinstance(attempt.traceback, str)

    @pytest.mark.asyncio
    async def test_valid_files_no_repair_needed(self, repair_service, build_critic, valid_generated_files):
        """Description: Valid files skip repair loop entirely."""
        final_files, attempts, success = await repair_service.repair_loop(
            valid_generated_files, build_critic
        )

        assert success
        assert len(attempts) == 0
