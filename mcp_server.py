"""
Lightweight MCP server that exposes RunTests and RunMutation to Claude Code.

Claude Code already has its own Read/Write/Bash — this server only provides
the two project-specific feedback tools so the comparison is fair across
all providers.

Usage (stdio, launched automatically by ClaudeCodeCLIProvider):
    python mcp_server.py --cwd /path/to/sandbox
"""

from __future__ import annotations

import argparse
import os
import sys

from mcp.server.fastmcp import FastMCP

# ── parse --cwd before FastMCP touches argv ────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--cwd", required=True, help="Sandbox working directory")
args, _remaining = parser.parse_known_args()
SANDBOX_CWD: str = os.path.abspath(args.cwd)

# ── server instance ────────────────────────────────────────────────────
mcp = FastMCP("arena-tools")


@mcp.tool()
def run_tests() -> str:
    """Run the project test suite via `make test`.

    Returns JSON with pass/fail status and full compiler + test output.
    Prefer this over invoking make directly — it gives structured results.
    """
    # Import lazily so the module can be parsed even without the skill on
    # PYTHONPATH (e.g. during `mcp dev` inspection).
    from skills.run_tests import execute

    return execute({}, SANDBOX_CWD)


@mcp.tool()
def run_mutation() -> str:
    """Run mutation testing with mutmut.

    Returns the mutation score (fraction of mutants killed) and the unified
    diffs of all surviving mutants.  Use the diffs to identify which code
    paths your tests do not exercise, then add targeted tests to kill those
    mutants.
    """
    from skills.run_mutation import execute

    return execute({}, SANDBOX_CWD)


if __name__ == "__main__":
    mcp.run(transport="stdio")
