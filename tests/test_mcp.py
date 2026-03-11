"""Tests for the MCP server and Claude Code MCP integration."""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# MCP server script structure
# ---------------------------------------------------------------------------

def test_mcp_server_script_exists():
    script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "mcp_server.py",
    )
    assert os.path.isfile(script)


# ---------------------------------------------------------------------------
# Claude Code provider — MCP config generation
# ---------------------------------------------------------------------------

from providers.claude_code import _write_mcp_config, _MCP_TOOL_NAMES, _MCP_SERVER_SCRIPT


def test_mcp_tool_names_mapping():
    assert "RunTests" in _MCP_TOOL_NAMES
    assert "RunMutation" in _MCP_TOOL_NAMES
    # Built-in skills should NOT be in the MCP map
    assert "Read" not in _MCP_TOOL_NAMES
    assert "Write" not in _MCP_TOOL_NAMES
    assert "Bash" not in _MCP_TOOL_NAMES


def test_mcp_server_script_path_points_to_file():
    assert os.path.isfile(_MCP_SERVER_SCRIPT)


def test_write_mcp_config_creates_valid_json(tmp_path):
    config_path = _write_mcp_config(str(tmp_path))
    try:
        with open(config_path) as f:
            data = json.load(f)
        # Must have our server entry
        assert "mcpServers" in data
        assert "arena-tools" in data["mcpServers"]
        srv = data["mcpServers"]["arena-tools"]
        assert srv["command"] == sys.executable
        assert "--cwd" in srv["args"]
        assert str(tmp_path) in srv["args"]
    finally:
        os.unlink(config_path)


def test_write_mcp_config_cleanup(tmp_path):
    """Config file can be deleted after use."""
    config_path = _write_mcp_config(str(tmp_path))
    os.unlink(config_path)
    assert not os.path.exists(config_path)


# ---------------------------------------------------------------------------
# Claude Code provider — allowed tools routing
# ---------------------------------------------------------------------------

def test_allowed_tools_split_correctly():
    """Read/Write/Bash stay native, RunTests/RunMutation get MCP prefix."""
    from providers.claude_code import _MCP_TOOL_NAMES

    allowed = ["Read", "Write", "Bash", "RunTests", "RunMutation"]
    cc_tools = []
    needs_mcp = False
    for skill in allowed:
        if skill in _MCP_TOOL_NAMES:
            cc_tools.append(f"mcp__arena-tools__{_MCP_TOOL_NAMES[skill]}")
            needs_mcp = True
        else:
            cc_tools.append(skill)

    assert needs_mcp is True
    assert "Read" in cc_tools
    assert "Write" in cc_tools
    assert "Bash" in cc_tools
    assert "mcp__arena-tools__run_tests" in cc_tools
    assert "mcp__arena-tools__run_mutation" in cc_tools
    # Original skill names for MCP tools should NOT appear
    assert "RunTests" not in cc_tools
    assert "RunMutation" not in cc_tools


def test_no_mcp_when_only_builtins():
    """If allowed_tools only has Read/Write/Bash, MCP is not needed."""
    from providers.claude_code import _MCP_TOOL_NAMES

    allowed = ["Read", "Write", "Bash"]
    needs_mcp = False
    for skill in allowed:
        if skill in _MCP_TOOL_NAMES:
            needs_mcp = True

    assert needs_mcp is False
