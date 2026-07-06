"""ReAct loop engine."""

from __future__ import annotations

from dataclasses import dataclass

from agentintelligence.context.manager import ConversationContext
from agentintelligence.loop.parser import parse_action
from agentintelligence.models.chat import ChatModel
from agentintelligence.tools.registry import FINISH_ACTION, ToolRegistry


@dataclass(frozen=True)
class AgentStep:
    action: str
    observation: str


@dataclass(frozen=True)
class AgentResult:
    finished: bool
    message: str
    steps: list[AgentStep]


class ReActLoop:
    """Generic observe-act loop that delegates reasoning to a chat model."""

    def __init__(
        self,
        model: ChatModel,
        registry: ToolRegistry,
        context: ConversationContext,
        max_steps: int = 20,
    ) -> None:
        self._model = model
        self._registry = registry
        self._context = context
        self._max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        self._context.start_task(task)
        steps: list[AgentStep] = []

        for _ in range(self._max_steps):
            raw_action = self._model.chat(self._context.to_messages())
            self._context.append_assistant(raw_action)

            try:
                action = parse_action(raw_action)
            except ValueError as exc:
                return AgentResult(False, str(exc), steps)

            action_name = action.get("action", "")
            if action_name == FINISH_ACTION:
                message = action.get("message", "")
                steps.append(AgentStep(action=FINISH_ACTION, observation=message))
                return AgentResult(True, message, steps)

            observation = self._registry.dispatch(action)
            steps.append(AgentStep(action=action_name, observation=observation))
            self._context.append_observation(observation)

        return AgentResult(False, "maximum agent steps reached", steps)
