"""
Telegram Gateway: accepts updates, routes by chat_id/thread_id, sends responses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TelegramUpdate:
    update_id: int
    chat_id: str
    message_id: str
    message_type: str  # "voice", "text", "callback"
    payload: dict[str, Any] = field(default_factory=dict)
    text: str = ""
    voice_file_id: str = ""


class TelegramGateway:
    """Handles incoming Telegram updates and outgoing messages."""

    SUPPORTED_TYPES = {"voice", "text", "callback"}

    def __init__(self, bot_token: str, send_fn=None):
        self.bot_token = bot_token
        self.send_fn = send_fn or self._default_send
        self._sent_messages: list[dict] = []

    def parse_update(self, raw: dict[str, Any]) -> TelegramUpdate | None:
        """Parse raw Telegram update JSON into TelegramUpdate."""
        update_id = raw.get("update_id", 0)
        message = raw.get("message", {})
        callback_query = raw.get("callback_query")

        if callback_query:
            return TelegramUpdate(
                update_id=update_id,
                chat_id=str(callback_query.get("message", {}).get("chat", {}).get("id", "")),
                message_id=str(callback_query.get("message", {}).get("message_id", "")),
                message_type="callback",
                payload=callback_query,
                text=callback_query.get("data", ""),
            )

        chat_id = str(message.get("chat", {}).get("id", ""))
        message_id = str(message.get("message_id", ""))

        if "voice" in message:
            return TelegramUpdate(
                update_id=update_id,
                chat_id=chat_id,
                message_id=message_id,
                message_type="voice",
                payload=message,
                voice_file_id=message["voice"].get("file_id", ""),
            )
        elif "text" in message:
            return TelegramUpdate(
                update_id=update_id,
                chat_id=chat_id,
                message_id=message_id,
                message_type="text",
                payload=message,
                text=message["text"],
            )

        return None

    def is_supported_type(self, update: TelegramUpdate) -> bool:
        return update.message_type in self.SUPPORTED_TYPES

    async def send_message(self, chat_id: str, text: str, reply_markup: dict | None = None):
        msg = {"chat_id": chat_id, "text": text}
        if reply_markup:
            msg["reply_markup"] = reply_markup
        self._sent_messages.append(msg)
        await self.send_fn(msg)

    async def send_interrupt(
        self, chat_id: str, question: str, choices: list[str] | None = None
    ):
        reply_markup = None
        if choices:
            reply_markup = {
                "inline_keyboard": [
                    [{"text": c, "callback_data": c}] for c in choices
                ]
            }
        await self.send_message(chat_id, question, reply_markup)

    async def _default_send(self, msg: dict):
        pass
