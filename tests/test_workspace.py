import sys

import pytest

from agentintelligence.workspace import Workspace


def test_workspace_reads_writes_and_lists_files(tmp_path):
    workspace = Workspace(tmp_path)

    workspace.write_text("src/example.py", "print('hi')\n")

    assert workspace.read_text("src/example.py") == "print('hi')\n"
    assert "src/example.py" in workspace.list_files()


def test_workspace_rejects_paths_outside_root(tmp_path):
    workspace = Workspace(tmp_path)

    with pytest.raises(ValueError, match="outside workspace"):
        workspace.read_text("../secret.txt")


def test_workspace_runs_commands_in_root(tmp_path):
    workspace = Workspace(tmp_path, allow_commands=True)

    result = workspace.run_command(
        [sys.executable, "-c", "from pathlib import Path; Path('ok.txt').write_text('done')"]
    )

    assert result.exit_code == 0
    assert result.stdout == ""
    assert workspace.read_text("ok.txt") == "done"


def test_workspace_disables_command_execution_by_default(tmp_path):
    workspace = Workspace(tmp_path)

    result = workspace.run_command(
        [sys.executable, "-c", "from pathlib import Path; Path('ok.txt').write_text('done')"]
    )

    assert result.exit_code == 126
    assert "disabled" in result.stderr
    assert "ok.txt" not in workspace.list_files()


def test_workspace_reports_command_timeout(tmp_path):
    workspace = Workspace(tmp_path, allow_commands=True)

    result = workspace.run_command(
        [sys.executable, "-c", "import time; time.sleep(2)"],
        timeout=1,
    )

    assert result.exit_code == 124
    assert "timed out" in result.stderr
