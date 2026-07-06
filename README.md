# agentintelligence

AgentIntelligence is a minimal coding agent powered by Aliyun Bailian GLM models.

The first version focuses on a reusable agent core plus a CLI wrapper:

- reads repository files
- writes files inside the workspace
- runs shell commands in the workspace
- asks an Aliyun Bailian GLM model for the next coding action
- iterates until the model returns a `finish` action

## Requirements

- Python 3.10+
- An Aliyun Bailian API key

Set one of these environment variables:

```bash
export BAILIAN_API_KEY="your-api-key"
# or
export DASHSCOPE_API_KEY="your-api-key"
```

Optional configuration:

```bash
export BAILIAN_MODEL="glm-4.5"
export BAILIAN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

## Install

```bash
python3 -m pip install -e '.[dev]'
```

## Run

```bash
agentintelligence "Read this repo and add a hello world script" --workspace .
```

Command execution is disabled by default. To let the agent run tests or other shell commands in the workspace, pass:

```bash
agentintelligence "Run the tests and fix failures" --workspace . --allow-command
```

`--allow-command` is not a sandbox. It only runs commands with the workspace as the current directory. Use it only in an isolated environment you trust.

If your shell cannot find the installed script, run the module directly:

```bash
python3 -m agentintelligence.cli "Read this repo and add a hello world script" --workspace .
```

## Agent action protocol

The model is instructed to return exactly one JSON action per step:

```json
{"action": "list_files"}
```

```json
{"action": "read_file", "path": "README.md"}
```

```json
{"action": "write_file", "path": "hello.py", "content": "print(\"hi\")\n"}
```

```json
{"action": "run_command", "command": "python3 hello.py"}
```

```json
{"action": "finish", "message": "summary"}
```