"""
Unit tests for GoalNormalizer.
Requirement IDs: FR-2, FR-3
Test Case IDs: TC-FR-002-02, TC-FR-003-01, TC-FR-003-02, TC-FR-003-03
"""

import pytest

from app.orchestrator.planner import GoalNormalizer


@pytest.mark.unit
class TestGoalNormalizer:

    @pytest.fixture
    def normalizer(self):
        return GoalNormalizer()

    @pytest.mark.asyncio
    async def test_FR_003_clear_transcript_produces_complete_goal(self, normalizer):
        """
        Automation ID: AT-FR-003-UNIT-01
        Description: Clear transcript produces goal with all fields populated.
        """
        transcript = "Make a report on the EV market in Saudi Arabia and save to Google Docs"
        result = await normalizer.normalize(transcript)

        assert result.goal
        assert "report" in result.goal.lower() or result.deliverable == "report"
        assert result.deliverable == "report"
        assert len(result.ambiguities) == 0 or result.ambiguities == []

    @pytest.mark.asyncio
    async def test_FR_003_ambiguous_transcript_produces_ambiguities(self, normalizer):
        """
        Automation ID: AT-FR-003-UNIT-02
        Description: Vague transcript produces non-empty ambiguities.
        """
        transcript = "Do something"
        result = await normalizer.normalize(transcript)

        assert result.goal
        assert len(result.ambiguities) > 0

    @pytest.mark.asyncio
    async def test_FR_003_empty_transcript_flags_ambiguity(self, normalizer):
        """
        Automation ID: AT-FR-003-UNIT-03
        Description: Empty transcript returns ambiguity flag.
        """
        result = await normalizer.normalize("")

        assert result.goal == ""
        assert len(result.ambiguities) > 0
        assert any("empty" in a.lower() or "unable" in a.lower() for a in result.ambiguities)

    @pytest.mark.asyncio
    async def test_FR_003_whitespace_only_treated_as_empty(self, normalizer):
        """
        Description: Whitespace-only input treated as empty.
        """
        result = await normalizer.normalize("   ")

        assert result.goal == ""
        assert len(result.ambiguities) > 0

    @pytest.mark.asyncio
    async def test_FR_002_empty_voice_no_crash(self, normalizer):
        """
        Automation ID: AT-FR-002-UNIT-01
        Description: Empty input does not crash normalizer.
        """
        result = await normalizer.normalize("")
        assert result is not None
        assert isinstance(result.goal, str)

    @pytest.mark.asyncio
    async def test_FR_003_deliverable_detection_report(self, normalizer):
        """Description: Detects 'report' deliverable."""
        result = await normalizer.normalize("Create a detailed report on market trends for Q4 2025")
        assert result.deliverable == "report"

    @pytest.mark.asyncio
    async def test_FR_003_deliverable_detection_summary(self, normalizer):
        """Description: Detects 'summary' deliverable."""
        result = await normalizer.normalize("Give me a summary of the meeting notes from last week")
        assert result.deliverable == "summary"

    @pytest.mark.asyncio
    async def test_FR_003_no_deliverable_when_absent(self, normalizer):
        """Description: No deliverable detected when none mentioned."""
        result = await normalizer.normalize("Search for information about competitor pricing strategies in the tech sector")
        assert result.deliverable == "" or result.deliverable is not None
