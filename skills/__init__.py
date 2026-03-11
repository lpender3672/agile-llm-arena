"""
Skills are the tool-calling primitives available to every provider.
Each skill lives in its own module with a DEFINITION dict and an execute() function.
The SKILLS registry here is the single source of truth for all providers.
"""

from . import bash, read, run_mutation, run_tests, write

_SKILL_MODULES = {
    "Read": read,
    "Write": write,
    "Bash": bash,
    "RunTests": run_tests,
    "RunMutation": run_mutation,
}

# Anthropic tool format — used by AnthropicAPIProvider directly
SKILLS: dict[str, dict] = {key: mod.DEFINITION for key, mod in _SKILL_MODULES.items()}

# Reverse map: API function name -> skill key, for dispatch after a tool call
FUNC_TO_SKILL: dict[str, str] = {v["name"]: k for k, v in SKILLS.items()}


def execute_skill(skill_key: str, inputs: dict, cwd: str) -> str:
    """Dispatch a skill call by key. Always returns a string result for the model."""
    mod = _SKILL_MODULES.get(skill_key)
    if mod is None:
        return f"Unknown skill: {skill_key}"
    try:
        return mod.execute(inputs, cwd)
    except Exception as exc:
        return f"ERROR: {exc}"


def to_openai_tool(skill_key: str) -> dict:
    """Convert a skill definition to OpenAI function-calling format."""
    s = SKILLS[skill_key]
    return {
        "type": "function",
        "function": {
            "name": s["name"],
            "description": s["description"],
            "parameters": s["input_schema"],
        },
    }
