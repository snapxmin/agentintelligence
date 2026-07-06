# Coding Agent GLM Design

## Goal

Build a first working version of AgentIntelligence as a CLI coding agent powered by Aliyun Bailian GLM models, while keeping the core reusable for later API and Web products.

## Scope

This first version includes:

- Aliyun Bailian OpenAI-compatible chat client.
- Workspace tools for listing, reading, writing, and optionally running commands from a repository.
- A small agent loop that asks the model for one JSON action at a time.
- CLI entry point that wires configuration, model, workspace, and agent together.

This version does not include multi-user authentication, background job queues, persistent task history, sandbox orchestration, or a Web UI. Those belong to later platform layers once the agent core is validated.

## Architecture

The project is split into a pluggable core and a thin CLI:

- `agentintelligence.models` defines the `ChatModel` protocol; `bailian.py` implements the Aliyun Bailian adapter.
- `agentintelligence.workspace` owns repository-scoped file and command operations used by tools.
- `agentintelligence.tools` defines the `Tool` protocol, concrete filesystem/shell tools, and `ToolRegistry`.
- `agentintelligence.context` owns conversation history and system prompt construction.
- `agentintelligence.loop` owns JSON action parsing and the generic `ReActLoop`.
- `agentintelligence.agent` wires model, registry, context, and loop together.
- `agentintelligence.cli` parses command-line arguments and runs the assembled agent.

The CLI, a future HTTP API, or a Web backend can all import the same `ReActLoop`, `ToolRegistry`, and `ConversationContext` primitives.

## Agent Protocol

The model receives a system prompt instructing it to return exactly one JSON object per step:

- `list_files`
- `read_file`
- `write_file`
- `run_command`
- `finish`

After each non-finish action, the agent executes the tool, appends an observation, and asks the model for the next action.

## Error Handling

The first version fails closed on invalid model JSON by returning an unfinished result with an explanatory message. Workspace paths are resolved under the configured root and path traversal outside that root is rejected.

Command execution is disabled by default because setting a command's current working directory is not a sandbox. CLI users must pass `--allow-command` to enable shell commands in an isolated environment. Tool errors such as missing files, rejected paths, missing action fields, and command timeouts are returned to the model as observations instead of crashing the agent loop.

## Testing

Tests cover:

- Bailian OpenAI-compatible request shape and environment configuration.
- Workspace file, command, and path-safety behavior.
- Tool registry dispatch and duplicate registration.
- Conversation context history and trimming.
- ReAct loop execution with registry-backed tools.
- Agent facade behavior, invalid JSON handling, and tool-error observations.
