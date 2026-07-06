import pytest

from agentintelligence.tools.registry import ToolRegistry


class EchoTool:
    name = "echo"

    def execute(self, params: dict[str, str]) -> str:
        return params.get("message", "")


class RequiredFieldTool:
    name = "required"

    def execute(self, params: dict[str, str]) -> str:
        if "value" not in params:
            raise ValueError("action requires string field: value")
        return params["value"]


def test_registry_dispatches_registered_tool():
    registry = ToolRegistry()
    registry.register(EchoTool())

    output = registry.dispatch({"action": "echo", "message": "hello"})

    assert output == "hello"


def test_registry_returns_unknown_action_message():
    registry = ToolRegistry()

    output = registry.dispatch({"action": "missing"})

    assert output == "unknown action: missing"


def test_registry_turns_tool_errors_into_observations():
    registry = ToolRegistry()
    registry.register(RequiredFieldTool())

    output = registry.dispatch({"action": "required"})

    assert output == "error: action requires string field: value"


def test_registry_rejects_duplicate_tool_names():
    registry = ToolRegistry()
    registry.register(EchoTool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(EchoTool())
