import subprocess

DEFINITION = {
    "name": "bash",
    "description": "Run a shell command in the project sandbox.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    },
}


def execute(inputs: dict, cwd: str) -> str:
    result = subprocess.run(
        inputs["command"], shell=True, cwd=cwd,
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout + result.stderr
