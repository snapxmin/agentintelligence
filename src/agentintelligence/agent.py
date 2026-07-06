"""Core coding agent loop."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from agentintelligence.workspace import Workspace


SYSTEM_PROMPT = """You are AgentIntelligence, a coding agent.
Work step by step inside the provided repository workspace.
Respond with exactly one JSON object per step, with one of these actions:
{"action": "list_files"}
{"action": "read_file", "path": "relative/path"}
{"action": "write_file", "path": "relative/path", "content": "full file content"}
{"action": "run_command", "command": "shell command"}
{"action": "finish", "message": "summary for the user"}
Do not include markdown around the JSON.
"""


class ChatModel(Protocol):
    def chat(self, messages: list[dict[str, str]]) -> str:
        """Return the model's next assistant message."""


@dataclass(frozen=True)
class AgentStep:
    action: str
    observation: str


@dataclass(frozen=True)
class AgentResult:
    finished: bool
    message: str
    steps: list[AgentStep]


class CodingAgent:
    """A small observe-act loop that delegates reasoning to a chat model."""

    def __init__(self, model: ChatModel, workspace: Workspace, max_steps: int = 20) -> None:
        self._model = model
        self._workspace = workspace
        self._max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ]
        steps: list[AgentStep] = []

        for _ in range(self._max_steps):
            raw_action = self._model.chat(messages)
            messages.append({"role": "assistant", "content": raw_action})

            try:
                action = _parse_action(raw_action)
            except ValueError as exc:
                return AgentResult(False, str(exc), steps)

            try:
                observation = self._execute(action)
            except (FileNotFoundError, OSError, ValueError) as exc:
                observation = "error: " + str(exc)
            steps.append(AgentStep(action=action["action"], observation=observation))

            if action["action"] == "finish":
                return AgentResult(True, action.get("message", ""), steps)

            messages.append({"role": "user", "content": "Observation:\n" + observation})

        return AgentResult(False, "maximum agent steps reached", steps)

    def _execute(self, action: dict[str, str]) -> str:
        name = action.get("action")
        if name == "list_files":
            return "\n".join(self._workspace.list_files())
        if name == "read_file":
            return self._workspace.read_text(_required(action, "path"))
        if name == "write_file":
            path = _required(action, "path")
            self._workspace.write_text(path, _required(action, "content"))
            return "wrote " + path
        if name == "run_command":
            result = self._workspace.run_command(_required(action, "command"))
            return (
                "exit_code: "
                + str(result.exit_code)
                + "\nstdout:\n"
                + result.stdout
                + "\nstderr:\n"
                + result.stderr
            )
        if name == "finish":
            return action.get("message", "")
        return "unknown action: " + str(name)


def _parse_action(raw_action: str) -> dict[str, str]:
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


def _required(action: dict[str, str], key: str) -> str:
    value = action.get(key)
    if not isinstance(value, str):
        raise ValueError("action requires string field: " + key)
    return value
