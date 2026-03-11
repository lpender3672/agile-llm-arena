import os

DEFINITION = {
    "name": "read_file",
    "description": "Read a file from the project sandbox.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path to the file"},
        },
        "required": ["path"],
    },
}


def execute(inputs: dict, cwd: str) -> str:
    path = os.path.join(cwd, inputs["path"])
    with open(path) as f:
        return f.read()
