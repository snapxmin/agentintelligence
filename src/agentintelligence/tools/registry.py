"""Tool registry and default tool wiring."""

from __future__ import annotations

from agentintelligence.tools.base import Tool
from agentintelligence.tools.filesystem import ListFilesTool, ReadFileTool, WriteFileTool
from agentintelligence.tools.shell import RunCommandTool
from agentintelligence.workspace import Workspace

FINISH_ACTION = "finish"


class ToolRegistry:
    """Dispatches model actions to registered tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError("tool already registered: " + tool.name)
        self._tools[tool.name] = tool

    def action_names(self) -> list[str]:
        names = sorted(self._tools.keys())
        if FINISH_ACTION not in names:
            names.append(FINISH_ACTION)
        return names

    def dispatch(self, action: dict[str, str]) -> str:
        name = action.get("action")
        tool = self._tools.get(name or "")
        if tool is None:
            return "unknown action: " + str(name)
        try:
            return tool.execute(action)
        except (FileNotFoundError, OSError, ValueError) as exc:
            return "error: " + str(exc)


def build_default_registry(workspace: Workspace) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ListFilesTool(workspace))
    registry.register(ReadFileTool(workspace))
    registry.register(WriteFileTool(workspace))
    if workspace.allow_commands:
        registry.register(RunCommandTool(workspace))
    return registry
