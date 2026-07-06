# Coding Agent GLM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal CLI coding agent powered by Aliyun Bailian GLM models.

**Architecture:** Implement a reusable Python core with a Bailian client, workspace tools, and an action-loop agent. Keep the CLI as a thin adapter so future API and Web layers can reuse the same core.

**Tech Stack:** Python 3.10+, stdlib HTTP via `urllib`, pytest for tests.

---

## File Structure

- `src/agentintelligence/bailian.py`: Bailian GLM OpenAI-compatible client and environment configuration.
- `src/agentintelligence/workspace.py`: Repository-scoped file tools and explicitly enabled command tools.
- `src/agentintelligence/agent.py`: JSON action protocol and observe-act loop.
- `src/agentintelligence/cli.py`: CLI argument parsing and runtime wiring.
- `tests/test_bailian_client.py`: Bailian client tests.
- `tests/test_workspace.py`: Workspace tool tests.
- `tests/test_agent.py`: Agent loop tests.
- `README.md`: Usage documentation.

### Task 1: Bailian GLM client

**Files:**
- Create: `src/agentintelligence/bailian.py`
- Test: `tests/test_bailian_client.py`

- [x] **Step 1: Write failing tests**

```python
def test_bailian_client_sends_openai_compatible_chat_request():
    captured = {}
    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()
    client = BailianGLMClient(BailianConfig(api_key="test-key", model="glm-test"), urlopen=fake_urlopen)
    assert client.chat([{"role": "user", "content": "Say hello."}]) == "hello from glm"
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest`

Expected: FAIL with `ModuleNotFoundError: No module named 'agentintelligence.bailian'`.

- [x] **Step 3: Write minimal implementation**

Implement `BailianConfig` and `BailianGLMClient.chat()` using Bailian's OpenAI-compatible `/chat/completions` endpoint.

- [x] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_bailian_client.py -v`

Expected: PASS.

### Task 2: Workspace tools

**Files:**
- Create: `src/agentintelligence/workspace.py`
- Test: `tests/test_workspace.py`

- [x] **Step 1: Write failing tests**

```python
def test_workspace_rejects_paths_outside_root(tmp_path):
    workspace = Workspace(tmp_path)
    with pytest.raises(ValueError, match="outside workspace"):
        workspace.read_text("../secret.txt")
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest`

Expected: FAIL with `ModuleNotFoundError: No module named 'agentintelligence.workspace'`.

- [x] **Step 3: Write minimal implementation**

Implement safe path resolution, text read/write, file listing, command execution default-off behavior, and command timeout handling.

- [x] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_workspace.py -v`

Expected: PASS.

### Task 3: Agent loop

**Files:**
- Create: `src/agentintelligence/agent.py`
- Test: `tests/test_agent.py`

- [x] **Step 1: Write failing tests**

```python
def test_agent_executes_model_actions_until_finish(tmp_path):
    workspace = Workspace(tmp_path)
    model = ScriptedModel([
        '{"action": "list_files"}',
        '{"action": "write_file", "path": "hello.py", "content": "print(\\"hi\\")\\n"}',
        '{"action": "finish", "message": "created hello.py"}',
    ])
    result = CodingAgent(model=model, workspace=workspace, max_steps=5).run("Create a file")
    assert result.finished is True
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest`

Expected: FAIL with `ModuleNotFoundError: No module named 'agentintelligence.agent'`.

- [x] **Step 3: Write minimal implementation**

Implement JSON parsing, action dispatch, observations, max-step handling, invalid JSON handling, and tool-error observations.

- [x] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_agent.py -v`

Expected: PASS.

### Task 4: CLI and docs

**Files:**
- Create: `src/agentintelligence/cli.py`
- Modify: `README.md`
- Modify: `pyproject.toml`

- [x] **Step 1: Add CLI entry point**

Create `agentintelligence.cli:main` that reads config, builds the agent, and prints each step.

- [x] **Step 2: Document usage**

Document environment variables, install command, run command, and JSON action protocol.

- [x] **Step 3: Run full verification**

Run: `python3 -m pytest`

Expected: all tests pass.
