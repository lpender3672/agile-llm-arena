import json
import time

from skills import SKILLS, FUNC_TO_SKILL, execute_skill, to_openai_tool
from .base import Provider, RunResult


class OpenAICompatProvider(Provider):
    """
    Base for any provider that speaks the OpenAI chat completions API with
    function-calling. Subclasses supply a configured AsyncOpenAI client.
    """

    def __init__(self, client, model_id: str):
        self.client = client
        self.model_id = model_id

    async def run(self, prompt, system, cwd, max_tokens, allowed_tools) -> RunResult:
        tools = [to_openai_tool(t) for t in allowed_tools if t in SKILLS]
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        total_input = total_output = turns = 0
        start = time.monotonic()
        output = ""

        while True:
            kwargs: dict = dict(
                model=self.model_id,
                messages=messages,
                max_tokens=min(4096, max_tokens - total_output),
            )
            if tools:
                kwargs["tools"] = tools

            resp = await self.client.chat.completions.create(**kwargs)
            msg = resp.choices[0].message
            total_input += resp.usage.prompt_tokens
            total_output += resp.usage.completion_tokens
            turns += 1

            if msg.content:
                output += msg.content

            if not getattr(msg, "tool_calls", None):
                break

            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })
            for tc in msg.tool_calls:
                skill_key = FUNC_TO_SKILL.get(tc.function.name, tc.function.name)
                result = execute_skill(skill_key, json.loads(tc.function.arguments), cwd)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

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
