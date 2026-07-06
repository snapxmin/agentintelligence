"""Tool interfaces."""

from __future__ import annotations

from typing import Protocol


class Tool(Protocol):
    @property
    def name(self) -> str:
        """Unique action name used by the model."""

    def execute(self, params: dict[str, str]) -> str:
        """Execute the tool and return an observation string."""
