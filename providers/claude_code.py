import asyncio
import json
import time

from .base import Provider, RunResult


class ClaudeCodeCLIProvider(Provider):
    """
    Invokes `claude -p` in headless mode.
    Requires the `claude` CLI on PATH and ANTHROPIC_API_KEY set.
    Skills are passed as --allowedTools; Claude Code resolves them internally.
    """

    async def run(self, prompt, system, cwd, max_tokens, allowed_tools) -> RunResult:
        cmd = [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--max-tokens", str(max_tokens),
        ]
        if system:
            cmd += ["--system", system]
        if allowed_tools:
            cmd += ["--allowedTools", ",".join(allowed_tools)]

        start = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        stdout, stderr = await proc.communicate()
        duration = time.monotonic() - start

        if proc.returncode != 0:
            return RunResult("", 0, 0, 0, duration, 0, error=stderr.decode())

        data = json.loads(stdout.decode())
        usage = data.get("usage", {})
        return RunResult(
            output=data.get("result", ""),
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            duration_seconds=duration,
            turns=data.get("num_turns", 1),
        )
