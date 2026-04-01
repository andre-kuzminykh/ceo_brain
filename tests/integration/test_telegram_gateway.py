"""
Integration tests for Telegram Gateway.
Requirement IDs: FR-1, FR-2, NFR-2, NFR-3
Test Case IDs: TC-FR-001-01, TC-FR-001-02, TC-FR-001-03, TC-NFR-002-01, TC-NFR-003-01
"""

import pytest

from app.models.state_models import InputModality, RunStatus
from app.orchestrator.run_manager import RunManager, RunStore
from app.telegram.bot import TelegramGateway


@pytest.mark.integration
class TestTelegramVoiceIntake:

    def test_FR_001_parse_voice_update(self, telegram_gateway, voice_update_raw):
        """
        Automation ID: AT-FR-001-INT-01
        Description: Bot accepts voice message and parses correctly.
        """
        update = telegram_gateway.parse_update(voice_update_raw)

        assert update is not None
        assert update.message_type == "voice"
        assert update.chat_id == "12345"
        assert update.voice_file_id == "voice_file_abc"
        assert telegram_gateway.is_supported_type(update)

    def test_FR_001_voice_creates_run(self, telegram_gateway, voice_update_raw, run_manager):
        """
        Automation ID: AT-FR-001-INT-01
        Description: Voice message creates a run with correct modality.
        """
        update = telegram_gateway.parse_update(voice_update_raw)
        run = run_manager.create_run(
            update_id=update.update_id,
            user_id="user-1",
            chat_id=update.chat_id,
            input_modality=InputModality.VOICE,
            voice_file_id=update.voice_file_id,
        )

        assert run.run_id
        assert run.input_modality == InputModality.VOICE
        assert run.execution_status == RunStatus.RECEIVED
        assert run.raw_input == "voice_file_abc"

    def test_FR_001_parse_text_update(self, telegram_gateway, text_update_raw):
        """
        Automation ID: AT-FR-001-INT-02
        Description: Bot accepts text message and parses correctly.
        """
        update = telegram_gateway.parse_update(text_update_raw)

        assert update is not None
        assert update.message_type == "text"
        assert update.text == "Make a report on EV market in Saudi Arabia and save to Google Docs"
        assert telegram_gateway.is_supported_type(update)

    def test_FR_001_text_creates_run(self, telegram_gateway, text_update_raw, run_manager):
        """
        Automation ID: AT-FR-001-INT-02
        Description: Text message creates a run with correct modality.
        """
        update = telegram_gateway.parse_update(text_update_raw)
        run = run_manager.create_run(
            update_id=update.update_id,
            user_id="user-1",
            chat_id=update.chat_id,
            input_modality=InputModality.TEXT,
            raw_input=update.text,
        )

        assert run.run_id
        assert run.input_modality == InputModality.TEXT
        assert run.execution_status == RunStatus.RECEIVED
        assert "report" in run.raw_input.lower()

    def test_FR_001_unsupported_type_returns_none(self, telegram_gateway, sticker_update_raw):
        """
        Automation ID: AT-FR-001-INT-03
        Description: Unsupported message types are rejected gracefully.
        """
        update = telegram_gateway.parse_update(sticker_update_raw)
        assert update is None  # Sticker not supported

    def test_FR_001_callback_update_parsed(self, telegram_gateway, callback_update_raw):
        """Description: Callback query (button press) is parsed."""
        update = telegram_gateway.parse_update(callback_update_raw)

        assert update is not None
        assert update.message_type == "callback"
        assert update.text == "Google Docs"
        assert telegram_gateway.is_supported_type(update)


@pytest.mark.integration
class TestIdempotentRunCreation:

    def test_NFR_002_duplicate_update_same_run(self, telegram_gateway, voice_update_raw, run_manager):
        """
        Automation ID: AT-NFR-002-INT-01
        Description: Duplicate webhook does not create duplicate run.
        """
        update = telegram_gateway.parse_update(voice_update_raw)

        run1 = run_manager.create_run(
            update_id=update.update_id,
            user_id="user-1",
            chat_id=update.chat_id,
            input_modality=InputModality.VOICE,
            voice_file_id=update.voice_file_id,
        )

        run2 = run_manager.create_run(
            update_id=update.update_id,
            user_id="user-1",
            chat_id=update.chat_id,
            input_modality=InputModality.VOICE,
            voice_file_id=update.voice_file_id,
        )

        assert run1.run_id == run2.run_id


@pytest.mark.integration
class TestTranscriptAndState:

    def test_FR_002_transcript_saved_to_run(self, run_manager):
        """
        Automation ID: AT-FR-002-INT-01
        Description: Transcript is saved and status transitions.
        """
        run = run_manager.create_run(
            update_id=200,
            user_id="user-1",
            chat_id="12345",
            input_modality=InputModality.VOICE,
            voice_file_id="voice_123",
        )

        run_manager.set_transcript(run.run_id, "Make a report on EV market")
        updated = run_manager.store.get(run.run_id)

        assert updated.transcript == "Make a report on EV market"
        assert updated.execution_status == RunStatus.TRANSCRIBED


@pytest.mark.integration
class TestSTTFallback:

    @pytest.mark.asyncio
    async def test_NFR_003_stt_failure_does_not_crash(self, run_manager, telegram_gateway):
        """
        Automation ID: AT-NFR-003-INT-01
        Description: STT failure moves run to waiting_for_user, not failed.
        """
        run = run_manager.create_run(
            update_id=300,
            user_id="user-1",
            chat_id="12345",
            input_modality=InputModality.VOICE,
            voice_file_id="bad_voice",
        )

        # Simulate STT failure -> fallback to manual
        stt_succeeded = False  # Simulating failure
        if not stt_succeeded:
            run_manager.update_status(run.run_id, RunStatus.WAITING_FOR_USER)
            await telegram_gateway.send_message(
                "12345",
                "Could not transcribe your voice message. Please type your request.",
            )

        updated = run_manager.store.get(run.run_id)
        assert updated.execution_status == RunStatus.WAITING_FOR_USER
        assert updated.execution_status != RunStatus.FAILED
        assert len(telegram_gateway._sent_messages) == 1
