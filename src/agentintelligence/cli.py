"""Command-line interface for AgentIntelligence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentintelligence.agent import CodingAgent
from agentintelligence.bailian import BailianConfig, BailianGLMClient
from agentintelligence.workspace import Workspace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a GLM-powered coding agent.")
    parser.add_argument("task", help="Coding task for the agent to perform.")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Repository/workspace path. Defaults to current directory.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
        help="Maximum model/tool iterations. Defaults to 20.",
    )
    parser.add_argument(
        "--allow-command",
        action="store_true",
        help="Allow the agent to run shell commands in the workspace.",
    )
    args = parser.parse_args(argv)

    config = BailianConfig.from_env()
    if not config.api_key:
        print(
            "Missing BAILIAN_API_KEY or DASHSCOPE_API_KEY for Aliyun Bailian.",
            file=sys.stderr,
        )
        return 2

    workspace = Workspace(Path(args.workspace), allow_commands=args.allow_command)
    agent = CodingAgent(
        model=BailianGLMClient(config),
        workspace=workspace,
        max_steps=args.max_steps,
    )
    result = agent.run(args.task)

    for index, step in enumerate(result.steps, start=1):
        print("Step %d: %s" % (index, step.action))
        if step.observation:
            print(step.observation)

    print(result.message)
    return 0 if result.finished else 1


if __name__ == "__main__":
    raise SystemExit(main())
