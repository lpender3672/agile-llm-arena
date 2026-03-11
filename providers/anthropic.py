import time

from skills import SKILLS, FUNC_TO_SKILL, execute_skill
from .base import Provider, RunResult


class AnthropicAPIProvider(Provider):
    """
    Anthropic Python SDK with full tool-calling loop.
    Requires: pip install anthropic  and  ANTHROPIC_API_KEY env var.
    """

    def __init__(self, model_id: str):
        import anthropic
        self.client = anthropic.AsyncAnthropic()
        self.model_id = model_id

    async def run(self, prompt, system, cwd, max_tokens, allowed_tools) -> RunResult:
        tools = [SKILLS[t] for t in allowed_tools if t in SKILLS]
        messages = [{"role": "user", "content": prompt}]
        total_input = total_output = turns = 0
        start = time.monotonic()
        output = ""

        while True:
            resp = await self.client.messages.create(
                model=self.model_id,
                max_tokens=min(4096, max_tokens - total_output),
                system=system,
                tools=tools,
                messages=messages,
            )
            total_input += resp.usage.input_tokens
            total_output += resp.usage.output_tokens
            turns += 1

            for block in resp.content:
                if block.type == "text":
                    output += block.text

            if resp.stop_reason != "tool_use":
                break

            tool_results = []
            for block in resp.content:
                if block.type != "tool_use":
                    continue
                skill_key = FUNC_TO_SKILL.get(block.name, block.name)
                result = execute_skill(skill_key, block.input, cwd)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": tool_results})

            if total_output >= max_tokens:
                break

        return RunResult(
            output=output,
            input_tokens=total_input,
            output_tokens=total_output,
            total_tokens=total_input + total_output,
            duration_seconds=time.monotonic() - start,
            turns=turns,
        )
