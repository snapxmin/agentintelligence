from agentintelligence.context.manager import ConversationContext
from agentintelligence.context.prompts import build_system_prompt
from agentintelligence.loop.react import ReActLoop
from agentintelligence.tools.registry import ToolRegistry
from agentintelligence.workspace import Workspace


class ScriptedModel(object):
    def __init__(self, replies):
        self.replies = list(replies)

    def chat(self, messages):
        return self.replies.pop(0)


class EchoTool:
    name = "echo"

    def execute(self, params: dict[str, str]) -> str:
        return params["message"]


def test_react_loop_runs_until_finish_action():
    registry = ToolRegistry()
    registry.register(EchoTool())
    context = ConversationContext(build_system_prompt(["echo", "finish"]))
    model = ScriptedModel(
        [
            '{"action": "echo", "message": "step-1"}',
            '{"action": "finish", "message": "done"}',
        ]
    )
    loop = ReActLoop(model=model, registry=registry, context=context, max_steps=5)

    result = loop.run("Say hello")

    assert result.finished is True
    assert result.message == "done"
    assert result.steps[0].observation == "step-1"


def test_react_loop_uses_workspace_tools_end_to_end(tmp_path):
    workspace = Workspace(tmp_path)
    from agentintelligence.tools.filesystem import ReadFileTool, WriteFileTool
    from agentintelligence.tools.registry import build_default_registry

    registry = build_default_registry(workspace)
    context = ConversationContext(build_system_prompt(registry.action_names()))
    model = ScriptedModel(
        [
            '{"action": "write_file", "path": "hello.py", "content": "print(\\"hi\\")\\n"}',
            '{"action": "finish", "message": "created hello.py"}',
        ]
    )
    loop = ReActLoop(model=model, registry=registry, context=context, max_steps=3)

    result = loop.run("Create hello.py")

    assert result.finished is True
    assert workspace.read_text("hello.py") == 'print("hi")\n'
