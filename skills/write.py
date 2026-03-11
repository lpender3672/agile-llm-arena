import os

DEFINITION = {
    "name": "write_file",
    "description": "Write content to a file in the project sandbox.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path to the file"},
            "content": {"type": "string", "description": "Full file content to write"},
        },
        "required": ["path", "content"],
    },
}


def execute(inputs: dict, cwd: str) -> str:
    path = os.path.join(cwd, inputs["path"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(inputs["content"])
    return "OK"
