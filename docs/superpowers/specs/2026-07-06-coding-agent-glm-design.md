# Coding Agent GLM Design

## Goal

Build a first working version of AgentIntelligence as a CLI coding agent powered by Aliyun Bailian GLM models, while keeping the core reusable for later API and Web products.

## Scope

This first version includes:

- Aliyun Bailian OpenAI-compatible chat client.
- Workspace tools for listing, reading, writing, and running commands inside a repository.
- A small agent loop that asks the model for one JSON action at a time.
- CLI entry point that wires configuration, model, workspace, and agent together.

This version does not include multi-user authentication, background job queues, persistent task history, sandbox orchestration, or a Web UI. Those belong to later platform layers once the agent core is validated.

## Architecture

The project is split into a reusable core and a thin CLI:

- `agentintelligence.bailian` owns Bailian GLM configuration and chat completion calls.
- `agentintelligence.workspace` owns repository-scoped file and command operations.
- `agentintelligence.agent` owns the observe-act loop and action protocol.
- `agentintelligence.cli` parses command-line arguments and runs the core agent.

The CLI uses the same core classes that a future HTTP API or Web backend can import.

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

## Testing

Tests cover:

- Bailian OpenAI-compatible request shape and environment configuration.
- Workspace file, command, and path-safety behavior.
- Agent action execution and invalid JSON handling.
