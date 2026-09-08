"""
run_mcp.py — Launcher for the VEGAS Pro & DaVinci Resolve MCP Server.

Configure in your MCP client (claude_desktop_config.json, Cursor, Antigravity):
{
  "mcpServers": {
    "vegas-resolve": {
      "command": "python",
      "args": ["c:\\Users\\Mi5a\\VegasDavinciLinkTool\\run_mcp.py"]
    }
  }
}
"""

import sys
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from vegas_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
