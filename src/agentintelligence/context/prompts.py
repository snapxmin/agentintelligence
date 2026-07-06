"""Prompt templates for the coding agent."""

from __future__ import annotations

ACTION_TEMPLATES = {
    "list_files": '{"action": "list_files"}',
    "read_file": '{"action": "read_file", "path": "relative/path"}',
    "write_file": '{"action": "write_file", "path": "relative/path", "content": "full file content"}',
    "run_command": '{"action": "run_command", "command": "shell command"}',
    "finish": '{"action": "finish", "message": "summary for the user"}',
}


def build_system_prompt(action_names: list[str]) -> str:
    lines = [
        "You are AgentIntelligence, a coding agent.",
        "Work step by step inside the provided repository workspace.",
        "Respond with exactly one JSON object per step, with one of these actions:",
    ]
    for action_name in action_names:
        template = ACTION_TEMPLATES.get(action_name)
        if template:
            lines.append(template)
    lines.append("Do not include markdown around the JSON.")
    return "\n".join(lines)
