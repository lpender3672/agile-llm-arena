from .base import Workflow

MUTATION_AWARE = Workflow(
    id="mutation_aware",
    description="Explicitly prompt for mutation-killing test design using the RunMutation skill",
    system_prompt=(
        "You are an expert in mutation testing for embedded C. "
        "Your goal is to write tests that kill as many mutants as possible. "
        "Think about: boundary values, operator mutations (< vs <=), "
        "sign flips, off-by-one errors, null pointer cases, overflow. "
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
2. Implement {spec['module']}.c.
3. Write tests specifically designed to kill mutants:
   - Test every boundary condition
   - Test operator variants (e.g. +1/-1 from boundaries)
   - Test null/zero/max inputs
   - Test each conditional branch independently
4. Call RunTests; fix any failures.
5. Call RunMutation. For each surviving mutant diff, add a test that kills it.
6. Repeat RunMutation until the score stops improving.
7. File: test/test_{spec['module']}.c
""",
    allowed_tools=["Read", "Write", "Bash", "RunTests", "RunMutation"],
)
