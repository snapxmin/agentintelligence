import json

from agentintelligence.bailian import BailianGLMClient, BailianConfig


class FakeResponse(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": "hello from glm",
                        }
                    }
                ]
            }
        ).encode("utf-8")


def test_bailian_client_sends_openai_compatible_chat_request():
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    client = BailianGLMClient(
        BailianConfig(
            api_key="test-key",
            model="glm-test",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=9,
        ),
        urlopen=fake_urlopen,
    )

    content = client.chat(
        [
            {"role": "system", "content": "You are a coding agent."},
            {"role": "user", "content": "Say hello."},
        ]
    )

    assert content == "hello from glm"
    assert captured["url"] == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    assert captured["timeout"] == 9
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["headers"]["Content-type"] == "application/json"
    assert captured["payload"] == {
        "model": "glm-test",
        "messages": [
            {"role": "system", "content": "You are a coding agent."},
            {"role": "user", "content": "Say hello."},
        ],
        "temperature": 0.2,
    }


def test_config_loads_from_bailian_environment(monkeypatch):
    monkeypatch.setenv("BAILIAN_API_KEY", "env-key")
    monkeypatch.setenv("BAILIAN_MODEL", "glm-env")
    monkeypatch.setenv("BAILIAN_BASE_URL", "https://example.test/v1")

    config = BailianConfig.from_env()

    assert config.api_key == "env-key"
    assert config.model == "glm-env"
    assert config.base_url == "https://example.test/v1"
