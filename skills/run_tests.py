import json
import subprocess

DEFINITION = {
    "name": "run_tests",
    "description": (
        "Run the project test suite via `make test`. "
        "Returns JSON with pass/fail status and full compiler + test output. "
        "Prefer this over invoking make directly — it gives structured results."
    ),
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


def execute(inputs: dict, cwd: str) -> str:
    try:
        result = subprocess.run(
            ["make", "test"], cwd=cwd,
            capture_output=True, text=True, timeout=60,
        )
        return json.dumps({
            "passed": result.returncode == 0,
            "output": (result.stdout + result.stderr)[:8000],
        })
    except FileNotFoundError:
        return json.dumps({"passed": False, "output": "ERROR: 'make' not found on PATH"})
    except subprocess.TimeoutExpired:
        return json.dumps({"passed": False, "output": "ERROR: make test timed out"})
