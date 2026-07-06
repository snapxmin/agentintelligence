from agentintelligence.context.manager import ConversationContext
from agentintelligence.context.prompts import build_system_prompt


def test_context_starts_with_system_prompt_and_task():
    context = ConversationContext(build_system_prompt(["list_files", "finish"]))

    context.start_task("Implement feature X")
    messages = context.to_messages()

    assert messages[0]["role"] == "system"
    assert "list_files" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "Implement feature X"}


def test_context_records_assistant_and_observation_messages():
    context = ConversationContext("system")
    context.start_task("task")

    context.append_assistant('{"action": "list_files"}')
    context.append_observation("README.md")

    messages = context.to_messages()

    assert messages[-2] == {"role": "assistant", "content": '{"action": "list_files"}'}
    assert messages[-1] == {"role": "user", "content": "Observation:\nREADME.md"}


def test_context_trims_old_messages_but_keeps_system_prompt():
    context = ConversationContext("system", max_messages=4)
    context.start_task("task")

    for index in range(6):
        context.append_assistant("assistant-%d" % index)
        context.append_observation("observation-%d" % index)

    messages = context.to_messages()

    assert messages[0] == {"role": "system", "content": "system"}
    assert len(messages) == 4
    assert messages[-1]["content"] == "Observation:\nobservation-5"
