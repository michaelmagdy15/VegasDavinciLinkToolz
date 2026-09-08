"""
test_mcp_server.py — Tests for the VEGAS Pro & DaVinci Resolve MCP Server.
"""

import pytest
from vegas_mcp.server import mcp, vegas_get_timeline_info, resolve_get_project_info


def test_mcp_server_initialization():
    assert mcp.name == "vegas-resolve-mcp"
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "vegas_get_timeline_info" in tool_names
    assert "vegas_scout_footage" in tool_names
    assert "vegas_get_selects_manifest" in tool_names
    assert "vegas_sync_to_resolve" in tool_names
    assert "resolve_sync_to_vegas" in tool_names
    assert "resolve_get_project_info" in tool_names


def test_vegas_get_timeline_info_structure():
    # Calling the tool should return a valid dict
    info = vegas_get_timeline_info()
    assert isinstance(info, dict)
    assert "status" in info


def test_resolve_get_project_info_structure():
    info = resolve_get_project_info()
    assert isinstance(info, dict)
    assert "status" in info
