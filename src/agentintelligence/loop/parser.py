"""Action parsing helpers."""

from __future__ import annotations

import json


def parse_action(raw_action: str) -> dict[str, str]:
    stripped = raw_action.strip()
    if stripped.startswith("```"):
        lines = [line for line in stripped.splitlines() if not line.strip().startswith("```")]
        stripped = "\n".join(lines).strip()
    try:
        decoded = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError("model must return a valid JSON action") from exc
    if not isinstance(decoded, dict) or "action" not in decoded:
        raise ValueError("model must return a valid JSON action")
    return decoded


def required_field(action: dict[str, str], key: str) -> str:
    value = action.get(key)
    if not isinstance(value, str):
        raise ValueError("action requires string field: " + key)
    return value
