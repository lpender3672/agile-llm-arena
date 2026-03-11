import json
import os
from unittest.mock import MagicMock, patch

import pytest

from skills import FUNC_TO_SKILL, SKILLS, execute_skill, to_openai_tool


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_skills_registry_has_expected_keys():
    assert set(SKILLS.keys()) == {"Read", "Write", "Bash", "RunTests", "RunMutation"}


def test_every_skill_has_required_fields():
    for key, defn in SKILLS.items():
        assert "name" in defn, f"{key} missing 'name'"
        assert "description" in defn, f"{key} missing 'description'"
        assert "input_schema" in defn, f"{key} missing 'input_schema'"


def test_func_to_skill_reverse_map():
    assert FUNC_TO_SKILL["read_file"] == "Read"
    assert FUNC_TO_SKILL["write_file"] == "Write"
    assert FUNC_TO_SKILL["bash"] == "Bash"
    assert FUNC_TO_SKILL["run_tests"] == "RunTests"
    assert FUNC_TO_SKILL["run_mutation"] == "RunMutation"


def test_func_to_skill_is_complete():
    # Every skill name should appear in the reverse map
    for key, defn in SKILLS.items():
        assert defn["name"] in FUNC_TO_SKILL, f"{key} not in FUNC_TO_SKILL"


# ---------------------------------------------------------------------------
# OpenAI tool format conversion
# ---------------------------------------------------------------------------

def test_to_openai_tool_structure():
    tool = to_openai_tool("Read")
    assert tool["type"] == "function"
    assert tool["function"]["name"] == "read_file"
    assert "description" in tool["function"]
    assert "parameters" in tool["function"]


@pytest.mark.parametrize("skill_key", list(SKILLS.keys()))
def test_to_openai_tool_all_skills(skill_key):
    tool = to_openai_tool(skill_key)
    assert tool["type"] == "function"
    assert tool["function"]["name"] == SKILLS[skill_key]["name"]


# ---------------------------------------------------------------------------
# execute_skill dispatch
# ---------------------------------------------------------------------------

def test_execute_skill_unknown_returns_error_string(sandbox):
    result = execute_skill("NonExistent", {}, sandbox)
    assert "Unknown skill" in result


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def test_read_existing_file(sandbox_with_file):
    result = execute_skill("Read", {"path": "hello.txt"}, sandbox_with_file)
    assert result == "hello world\n"


def test_read_missing_file_returns_error(sandbox):
    result = execute_skill("Read", {"path": "no_such_file.txt"}, sandbox)
    assert result.startswith("ERROR:")


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def test_write_creates_file(sandbox):
    execute_skill("Write", {"path": "out.txt", "content": "data"}, sandbox)
    with open(os.path.join(sandbox, "out.txt")) as f:
        assert f.read() == "data"


def test_write_creates_nested_dirs(sandbox):
    execute_skill("Write", {"path": "a/b/c.txt", "content": "nested"}, sandbox)
    assert os.path.exists(os.path.join(sandbox, "a", "b", "c.txt"))


def test_write_returns_ok(sandbox):
    result = execute_skill("Write", {"path": "f.txt", "content": ""}, sandbox)
    assert result == "OK"


def test_write_overwrites_existing_file(sandbox_with_file):
    execute_skill("Write", {"path": "hello.txt", "content": "new content"}, sandbox_with_file)
    with open(os.path.join(sandbox_with_file, "hello.txt")) as f:
        assert f.read() == "new content"


# ---------------------------------------------------------------------------
# Bash
# ---------------------------------------------------------------------------

def test_bash_runs_command(sandbox):
    result = execute_skill("Bash", {"command": "echo ping"}, sandbox)
    assert "ping" in result


def test_bash_captures_stderr(sandbox):
    result = execute_skill("Bash", {"command": "echo err >&2"}, sandbox)
    assert "err" in result


def test_bash_nonzero_exit_returns_output_not_exception(sandbox):
    # Should not raise — just return whatever output there was
    result = execute_skill("Bash", {"command": "exit 1"}, sandbox)
    assert isinstance(result, str)


def test_bash_uses_sandbox_cwd(sandbox):
    execute_skill("Write", {"path": "marker.txt", "content": "x"}, sandbox)
    result = execute_skill("Bash", {"command": "cat marker.txt"}, sandbox)
    assert "x" in result


# ---------------------------------------------------------------------------
# RunTests
# ---------------------------------------------------------------------------

def test_run_tests_returns_valid_json(sandbox):
    result = execute_skill("RunTests", {}, sandbox)
    data = json.loads(result)  # must be valid JSON regardless of environment
    assert "passed" in data
    assert "output" in data


def test_run_tests_reports_failure(sandbox):
    with patch("skills.run_tests.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="FAIL\n", stderr="")
        data = json.loads(execute_skill("RunTests", {}, sandbox))
    assert data["passed"] is False
    assert "FAIL" in data["output"]


def test_run_tests_reports_success(sandbox):
    with patch("skills.run_tests.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="ALL TESTS PASSED\n", stderr="")
        data = json.loads(execute_skill("RunTests", {}, sandbox))
    assert data["passed"] is True
    assert "ALL TESTS PASSED" in data["output"]


def test_run_tests_output_truncated_at_8000_chars(sandbox):
    with patch("skills.run_tests.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="x" * 10000, stderr="")
        data = json.loads(execute_skill("RunTests", {}, sandbox))
    assert len(data["output"]) <= 8000


def test_run_tests_make_not_found_returns_json(sandbox):
    with patch("skills.run_tests.subprocess.run", side_effect=FileNotFoundError):
        data = json.loads(execute_skill("RunTests", {}, sandbox))
    assert data["passed"] is False
    assert "make" in data["output"].lower()
