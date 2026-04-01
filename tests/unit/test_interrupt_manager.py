"""
Unit tests for InterruptManager and response validation.
Requirement IDs: FR-9, FR-10, NFR-4
Test Case IDs: TC-FR-009-01, TC-FR-010-01, TC-FR-010-02, TC-FR-010-03
"""

import pytest

from app.models.state_models import InterruptPayload
from app.orchestrator.runtime_executor import InterruptManager


@pytest.mark.unit
class TestInterruptManager:

    def test_create_and_get_interrupt(self, interrupt_manager, interrupt_payload_choice):
        """Description: Interrupt can be created and retrieved."""
        interrupt_manager.create_interrupt("run-1", interrupt_payload_choice)
        pending = interrupt_manager.get_pending("run-1")
        assert pending is not None
        assert pending.question == "Which format do you prefer?"

    def test_no_pending_returns_none(self, interrupt_manager):
        """Description: Non-existent run returns None."""
        assert interrupt_manager.get_pending("nonexistent") is None

    def test_FR_010_valid_choice_resolves(self, interrupt_manager, interrupt_payload_choice):
        """
        Automation ID: AT-FR-010-UNIT-01
        Description: Valid choice response maps to state update.
        """
        interrupt_manager.create_interrupt("run-1", interrupt_payload_choice)
        result = interrupt_manager.resolve("run-1", "Google Docs", "choice")

        assert result["field"] == "delivery_format"
        assert result["value"] == "Google Docs"

    def test_FR_010_invalid_choice_rejected(self, interrupt_manager, interrupt_payload_choice):
        """
        Automation ID: AT-FR-010-UNIT-02
        Description: Invalid choice is rejected with error.
        """
        interrupt_manager.create_interrupt("run-1", interrupt_payload_choice)

        with pytest.raises(ValueError, match="Invalid choice"):
            interrupt_manager.resolve("run-1", "Slack", "choice")

    def test_FR_010_free_text_accepted(self, interrupt_manager, interrupt_payload_text):
        """
        Automation ID: AT-FR-010-UNIT-03
        Description: Free text response accepted for text-type interrupts.
        """
        interrupt_manager.create_interrupt("run-1", interrupt_payload_text)
        result = interrupt_manager.resolve("run-1", "Focus on consumer segment only", "text")

        assert result["field"] == "report_focus"
        assert result["value"] == "Focus on consumer segment only"

    def test_FR_010_empty_text_rejected(self, interrupt_manager, interrupt_payload_text):
        """Description: Empty text response is rejected."""
        interrupt_manager.create_interrupt("run-1", interrupt_payload_text)

        with pytest.raises(ValueError, match="empty"):
            interrupt_manager.resolve("run-1", "   ", "text")

    def test_resolve_nonexistent_interrupt_raises(self, interrupt_manager):
        """Description: Resolving non-existent interrupt raises error."""
        with pytest.raises(ValueError, match="No pending interrupt"):
            interrupt_manager.resolve("nonexistent", "response")

    def test_resolve_removes_pending(self, interrupt_manager, interrupt_payload_choice):
        """Description: Resolved interrupt is removed from pending."""
        interrupt_manager.create_interrupt("run-1", interrupt_payload_choice)
        interrupt_manager.resolve("run-1", "PDF")
        assert interrupt_manager.get_pending("run-1") is None
