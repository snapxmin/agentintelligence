"""Shell command tool backed by the workspace sandbox."""

from __future__ import annotations

from agentintelligence.loop.parser import required_field
from agentintelligence.workspace import Workspace


class RunCommandTool:
    name = "run_command"

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def execute(self, params: dict[str, str]) -> str:
        result = self._workspace.run_command(required_field(params, "command"))
        return (
            "exit_code: "
            + str(result.exit_code)
            + "\nstdout:\n"
            + result.stdout
            + "\nstderr:\n"
            + result.stderr
        )
