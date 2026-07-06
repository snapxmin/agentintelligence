"""Conversation context management."""

from __future__ import annotations


class ConversationContext:
    """Stores and trims the message history sent to the model."""

    def __init__(self, system_prompt: str, max_messages: int | None = None) -> None:
        self._system_prompt = system_prompt
        self._max_messages = max_messages
        self._messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]

    def start_task(self, task: str) -> None:
        self._messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": task},
        ]

    def append_assistant(self, content: str) -> None:
        self._messages.append({"role": "assistant", "content": content})
        self._maybe_trim()

    def append_observation(self, observation: str) -> None:
        self._messages.append({"role": "user", "content": "Observation:\n" + observation})
        self._maybe_trim()

    def to_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def _maybe_trim(self) -> None:
        if self._max_messages is None or len(self._messages) <= self._max_messages:
            return
        # Keep the system prompt and the most recent messages.
        system_message = self._messages[0]
        recent_messages = self._messages[-(self._max_messages - 1) :]
        self._messages = [system_message] + recent_messages
