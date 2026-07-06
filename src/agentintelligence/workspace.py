"""Repository workspace tools for the coding agent."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


class Workspace:
    """Safe file and command operations scoped to one repository root."""

    def __init__(self, root: str | Path, allow_commands: bool = False) -> None:
        self.root = Path(root).resolve()
        self.allow_commands = allow_commands

    def read_text(self, path: str) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def write_text(self, path: str, content: str) -> None:
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

    def list_files(self) -> list[str]:
        ignored_parts = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
        files: list[str] = []
        for candidate in self.root.rglob("*"):
            relative = candidate.relative_to(self.root)
            if any(part in ignored_parts for part in relative.parts):
                continue
            if candidate.is_file():
                files.append(relative.as_posix())
        return sorted(files)

    def run_command(
        self,
        command: str | Sequence[str],
        timeout: int = 120,
    ) -> CommandResult:
        if not self.allow_commands:
            return CommandResult(
                exit_code=126,
                stdout="",
                stderr="command execution is disabled; rerun with explicit command permission",
            )
        try:
            completed = subprocess.run(
                command,
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=timeout,
                shell=isinstance(command, str),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                exit_code=124,
                stdout=_output_to_text(exc.stdout),
                stderr="command timed out after " + str(timeout) + " seconds",
            )
        return CommandResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def _resolve(self, path: str) -> Path:
        resolved = (self.root / path).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("path is outside workspace: " + path) from exc
        return resolved


def _output_to_text(output: str | bytes | None) -> str:
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output
