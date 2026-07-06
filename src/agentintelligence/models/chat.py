"""Chat model protocol."""

from __future__ import annotations

from typing import Protocol


class ChatModel(Protocol):
    def chat(self, messages: list[dict[str, str]]) -> str:
        """Return the model's next assistant message."""
