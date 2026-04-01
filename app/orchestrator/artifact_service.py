"""
Artifact & Delivery Service.
"""

from __future__ import annotations

from typing import Any

from app.models.state_models import Artifact, CriticVerdict


class ArtifactService:
    """Creates and delivers artifacts to external systems."""

    def __init__(self, google_docs_writer=None):
        self.google_docs_writer = google_docs_writer
        self._delivered: list[Artifact] = []

    def create_artifact(
        self,
        artifact_type: str,
        content: dict[str, Any],
    ) -> Artifact:
        return Artifact(
            artifact_type=artifact_type,
            content=content,
        )

    async def deliver(
        self,
        artifact: Artifact,
        destination: str = "google_docs",
        critic_verdict: CriticVerdict | None = None,
    ) -> Artifact:
        """Deliver artifact only if critic has passed."""
        if critic_verdict is not None and critic_verdict != CriticVerdict.PASS:
            raise ValueError(
                f"Cannot deliver artifact: critic verdict is {critic_verdict.value}, expected pass"
            )

        if destination == "google_docs":
            artifact = await self._write_to_google_docs(artifact)
        elif destination == "telegram":
            artifact.delivery_status = "sent"
        else:
            raise ValueError(f"Unknown destination: {destination}")

        self._delivered.append(artifact)
        return artifact

    async def _write_to_google_docs(self, artifact: Artifact) -> Artifact:
        if self.google_docs_writer:
            url = await self.google_docs_writer(artifact.content)
            artifact.artifact_url = url
            artifact.delivery_status = "sent"
        else:
            raise RuntimeError("Google Docs writer not configured")
        return artifact
