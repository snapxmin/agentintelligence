"""Filesystem tools backed by the workspace sandbox."""

from __future__ import annotations

from agentintelligence.loop.parser import required_field
from agentintelligence.workspace import Workspace


class ListFilesTool:
    name = "list_files"

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def execute(self, params: dict[str, str]) -> str:
        return "\n".join(self._workspace.list_files())


class ReadFileTool:
    name = "read_file"

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def execute(self, params: dict[str, str]) -> str:
        return self._workspace.read_text(required_field(params, "path"))


class WriteFileTool:
    name = "write_file"

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def execute(self, params: dict[str, str]) -> str:
        path = required_field(params, "path")
        self._workspace.write_text(path, required_field(params, "content"))
        return "wrote " + path
