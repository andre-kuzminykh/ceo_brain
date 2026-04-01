"""
Run Manager: creates, persists, and retrieves runs.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.models.state_models import InputModality, RunState, RunStatus


class RunStore:
    """In-memory run store (replaced by DB in production)."""

    def __init__(self):
        self._runs: dict[str, RunState] = {}
        self._update_index: dict[int, str] = {}  # update_id -> run_id

    def get(self, run_id: str) -> RunState | None:
        return self._runs.get(run_id)

    def get_by_update_id(self, update_id: int) -> RunState | None:
        run_id = self._update_index.get(update_id)
        if run_id:
            return self._runs.get(run_id)
        return None

    def save(self, run: RunState, update_id: int | None = None):
        self._runs[run.run_id] = run
        if update_id is not None:
            self._update_index[update_id] = run.run_id

    def list_by_user(self, user_id: str) -> list[RunState]:
        return [r for r in self._runs.values() if r.user_id == user_id]


class RunManager:
    """Creates and manages run lifecycle."""

    def __init__(self, store: RunStore):
        self.store = store

    def create_run(
        self,
        update_id: int,
        user_id: str,
        chat_id: str,
        input_modality: InputModality,
        raw_input: str = "",
        voice_file_id: str = "",
    ) -> RunState:
        # Idempotency: check if run already exists for this update
        existing = self.store.get_by_update_id(update_id)
        if existing:
            return existing

        run = RunState(
            run_id=str(uuid.uuid4()),
            user_id=user_id,
            chat_id=chat_id,
            thread_id=f"thread-{chat_id}-{update_id}",
            input_modality=input_modality,
            raw_input=raw_input or voice_file_id,
            execution_status=RunStatus.RECEIVED,
        )
        self.store.save(run, update_id)
        return run

    def update_status(self, run_id: str, status: RunStatus) -> RunState | None:
        run = self.store.get(run_id)
        if run:
            run.execution_status = status
            self.store.save(run)
        return run

    def set_transcript(self, run_id: str, transcript: str) -> RunState | None:
        run = self.store.get(run_id)
        if run:
            run.transcript = transcript
            run.execution_status = RunStatus.TRANSCRIBED
            self.store.save(run)
        return run
