from .base import Workflow

IMPL_FIRST = Workflow(
    id="impl_first",
    description="Implement fully, then write tests to validate",
    system_prompt=(
        "You are an expert embedded C developer. "
        "Write clean, defensive implementations first, then validate with tests. "
        "Use Unity test framework."
    ),
    build_prompt=lambda spec: f"""Project: {spec['name']}
Description: {spec['description']}

Existing files:
{spec['file_tree']}

Specification:
{spec['spec']}

Task:
1. Read the existing files.
2. Implement {spec['module']}.c fully, handling all edge cases.
3. Write Unity tests in test/test_{spec['module']}.c.
4. Call RunTests and fix any failures.
""",
    allowed_tools=["Read", "Write", "Bash", "RunTests"],
)
