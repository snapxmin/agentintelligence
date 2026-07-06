from agentintelligence.agent import CodingAgent
from agentintelligence.workspace import Workspace


class ScriptedModel(object):
    def __init__(self, replies):
        self.replies = list(replies)
        self.messages_seen = []

    def chat(self, messages):
        self.messages_seen.append(list(messages))
        return self.replies.pop(0)


def test_agent_executes_model_actions_until_finish(tmp_path):
    workspace = Workspace(tmp_path)
    model = ScriptedModel(
        [
            '{"action": "list_files"}',
            '{"action": "write_file", "path": "hello.py", "content": "print(\\"hi\\")\\n"}',
            '{"action": "read_file", "path": "hello.py"}',
            '{"action": "finish", "message": "created hello.py"}',
        ]
    )
    agent = CodingAgent(model=model, workspace=workspace, max_steps=5)

    result = agent.run("Create a hello.py file")

    assert result.finished is True
    assert result.message == "created hello.py"
    assert workspace.read_text("hello.py") == 'print("hi")\n'
    assert len(result.steps) == 4
    assert result.steps[1].action == "write_file"


def test_agent_reports_invalid_model_action(tmp_path):
    workspace = Workspace(tmp_path)
    model = ScriptedModel(["not json"])
    agent = CodingAgent(model=model, workspace=workspace, max_steps=1)

    result = agent.run("Do something")

    assert result.finished is False
    assert "valid JSON" in result.message
