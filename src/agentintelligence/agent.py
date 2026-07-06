"""Assembles the pluggable coding agent core."""

from __future__ import annotations

from agentintelligence.context.manager import ConversationContext
from agentintelligence.context.prompts import build_system_prompt
from agentintelligence.loop.react import AgentResult, AgentStep, ReActLoop
from agentintelligence.models.chat import ChatModel
from agentintelligence.tools.base import Tool
from agentintelligence.tools.registry import build_default_registry
from agentintelligence.workspace import Workspace

__all__ = ["AgentResult", "AgentStep", "ChatModel", "CodingAgent"]


class CodingAgent:
    """High-level facade that wires model, tools, context, and loop together."""

    def __init__(
        self,
        model: ChatModel,
        workspace: Workspace,
        max_steps: int = 20,
        max_messages: int | None = None,
        extra_tools: list[Tool] | None = None,
    ) -> None:
        self._workspace = workspace
        self._registry = build_default_registry(workspace)
        if extra_tools:
            for tool in extra_tools:
                self._registry.register(tool)
        system_prompt = build_system_prompt(self._registry.action_names())
        context = ConversationContext(system_prompt, max_messages=max_messages)
        self._loop = ReActLoop(
            model=model,
            registry=self._registry,
            context=context,
            max_steps=max_steps,
        )

    @property
    def registry(self):
        return self._registry

    def run(self, task: str) -> AgentResult:
        return self._loop.run(task)
