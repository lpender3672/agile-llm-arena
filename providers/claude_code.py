import asyncio
import json
import os
import sys
import tempfile
import time

from .base import Provider, RunResult

# Maps our skill names → MCP tool names exposed by mcp_server.py.
# Claude Code's built-in tools (Read, Write, Bash) are not listed here —
# they are always available and handled internally by Claude Code.
_MCP_TOOL_NAMES = {"RunTests": "run_tests", "RunMutation": "run_mutation"}

# Absolute path to the MCP server script (sibling of this package).
_MCP_SERVER_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "mcp_server.py",
)


def _write_mcp_config(cwd: str) -> str:
    """Write a temporary mcp.json that tells Claude Code about our tools.

    Returns the path to the temp file (caller should clean up).
    """
    config = {
        "mcpServers": {
            "arena-tools": {
                "command": sys.executable,
                "args": [_MCP_SERVER_SCRIPT, "--cwd", os.path.abspath(cwd)],
            }
        }
    }
    fd, path = tempfile.mkstemp(suffix=".json", prefix="arena_mcp_")
    with os.fdopen(fd, "w") as f:
        json.dump(config, f)
    return path


class ClaudeCodeCLIProvider(Provider):
    """
    Invokes ``claude -p`` in headless mode.

    Requires the ``claude`` CLI on PATH and ANTHROPIC_API_KEY set.

    Built-in Claude Code tools (Read, Write, Bash, etc.) are always available.
    Our custom feedback tools (RunTests / RunMutation) are served via a
    lightweight MCP server that is started automatically for each run.
    """

    async def run(self, prompt, system, cwd, max_tokens, allowed_tools) -> RunResult:
        # ── build the --allowedTools list ───────────────────────────────
        # Keep Claude Code built-ins that map to our skill names, and add
        # the MCP-served tools with the "mcp__arena-tools__" prefix.
        cc_tools: list[str] = []
        needs_mcp = False

        for skill in (allowed_tools or []):
            if skill in _MCP_TOOL_NAMES:
                cc_tools.append(f"mcp__arena-tools__{_MCP_TOOL_NAMES[skill]}")
                needs_mcp = True
            else:
                # Read / Write / Bash → Claude Code resolves natively
                cc_tools.append(skill)

        # ── optional MCP config ────────────────────────────────────────
        mcp_config_path: str | None = None
        if needs_mcp:
            mcp_config_path = _write_mcp_config(cwd)

        cmd = [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--max-tokens", str(max_tokens),
        ]
        if system:
            cmd += ["--system", system]
        if cc_tools:
            cmd += ["--allowedTools", ",".join(cc_tools)]
        if mcp_config_path:
            cmd += ["--mcp-config", mcp_config_path]

        start = time.monotonic()
        try:
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
        finally:
            if mcp_config_path:
                try:
                    os.unlink(mcp_config_path)
                except OSError:
                    pass
