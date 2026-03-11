from .base import Workflow

ITERATIVE = Workflow(
    id="iterative",
    description="Implement and test in small incremental loops",
    system_prompt=(
        "You are an expert embedded C developer. "
        "Work incrementally: implement one function, write its tests, verify, repeat. "
        "Use Unity test framework. Call RunTests frequently."
    ),
    build_prompt=lambda spec: f"""Project: {spec['name']}
Description: {spec['description']}

Existing files:
{spec['file_tree']}

Specification:
{spec['spec']}

Task:
Work through the specification function by function:
- For each function: implement it, write its tests, call RunTests, fix failures.
- Only move to the next function when the current one passes.
- Module: {spec['module']}.c
""",
    allowed_tools=["Read", "Write", "Bash", "RunTests"],
)
