from .base import Workflow

TDD = Workflow(
    id="tdd",
    description="Write failing tests first, then implement to make them pass",
    system_prompt=(
        "You are an expert embedded C developer practicing strict TDD. "
        "Always write tests before implementation. "
        "Use Unity test framework. "
        "Call RunTests after each change. "
        "Do not move on until tests pass."
    ),
    build_prompt=lambda spec: f"""Project: {spec['name']}
Description: {spec['description']}

Existing files:
{spec['file_tree']}

Specification:
{spec['spec']}

Task:
1. Read the existing source files to understand the skeleton.
2. Write comprehensive Unity tests in test/test_{spec['module']}.c covering all edge cases.
3. Implement {spec['module']}.c to make all tests pass.
4. Call RunTests and fix any failures.
5. Aim for maximum mutation kill rate — think about boundary values, overflow, off-by-one.
""",
    allowed_tools=["Read", "Write", "Bash", "RunTests"],
)
