"""
vegas_mcp/server.py — Official Model Context Protocol (MCP) Server for VEGAS Pro & DaVinci Resolve.

Enables LLMs (Claude, Antigravity, Cursor) to inspect, scout footage,
and execute bidirectional live synchronization between VEGAS Pro and DaVinci Resolve.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

# Ensure repository root is on sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from core.live_bridge import (
    get_resolve_app,
    is_resolve_running,
    get_current_project_info,
    import_timeline_from_json,
    export_timeline_to_json,
)
from core.ai_scout import scout_directory, export_selects_manifest

# Initialize FastMCP Server
mcp = FastMCP("vegas-resolve-mcp")


@mcp.tool()
def vegas_get_timeline_info() -> Dict[str, Any]:
    """Inspect the active VEGAS Pro timeline manifest including tracks, clips, markers, and duration."""
    bridge_dir = Path.home() / ".timeline_bridge"
    json_path = bridge_dir / "vegas_timeline.json"

    if not json_path.exists():
        return {
            "status": "error",
            "message": "No VEGAS timeline manifest found. In VEGAS Pro, click 'Tools -> Scripting -> Send to DaVinci Resolve' to export the current project.",
        }

    try:
        with open(json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        tracks_summary = []
        total_clips = 0
        for t in data.get("tracks", []):
            clips = t.get("clips", [])
            total_clips += len(clips)
            tracks_summary.append({
                "name": t.get("name"),
                "is_video": t.get("is_video"),
                "is_audio": t.get("is_audio"),
                "clip_count": len(clips),
                "mute": t.get("mute"),
            })

        return {
            "status": "success",
            "project_name": data.get("project_name", "Untitled"),
            "frame_rate": data.get("frame_rate", 29.97),
            "width": data.get("width", 1920),
            "height": data.get("height", 1080),
            "total_clips": total_clips,
            "markers_count": len(data.get("markers", [])),
            "regions_count": len(data.get("regions", [])),
            "tracks": tracks_summary,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to read VEGAS manifest: {e}"}


@mcp.tool()
def vegas_scout_footage(folder_path: str, target_duration_s: float = 2.5) -> Dict[str, Any]:
    """Analyze a directory of video clips with Vision & Motion detection to find peak action moments.

    Args:
        folder_path: Absolute path to the folder containing video clips (or proxy folder).
        target_duration_s: Desired length for each action sub-clip in seconds (default: 2.5s).
    """
    if not os.path.exists(folder_path):
        return {"status": "error", "message": f"Directory does not exist: {folder_path}"}

    selects = scout_directory(folder_path, log_fn=lambda msg: None)
    if not selects:
        return {"status": "warning", "message": "No video files found or analyzed."}

    manifest_path = export_selects_manifest(selects, manifest_name=f"Selects from {Path(folder_path).name}")

    return {
        "status": "success",
        "scouted_folder": folder_path,
        "cuts_detected": len(selects),
        "manifest_path": manifest_path,
        "sample_cuts": selects[:5],
    }


@mcp.tool()
def vegas_get_selects_manifest() -> Dict[str, Any]:
    """Retrieve the latest AI Selects manifest with pre-trimmed action timestamps."""
    bridge_dir = Path.home() / ".timeline_bridge"
    manifest_path = bridge_dir / "ai_selects_manifest.json"

    if not manifest_path.exists():
        return {"status": "error", "message": "No AI selects manifest found. Run vegas_scout_footage first."}

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "status": "success",
        "manifest_name": data.get("manifest_name"),
        "clip_count": data.get("clip_count"),
        "clips": data.get("clips", []),
    }


@mcp.tool()
def vegas_sync_to_resolve() -> Dict[str, Any]:
    """Execute live synchronization of the VEGAS Pro timeline into DaVinci Resolve Studio."""
    bridge_dir = Path.home() / ".timeline_bridge"
    json_path = bridge_dir / "vegas_timeline.json"

    if not json_path.exists():
        return {"status": "error", "message": "vegas_timeline.json not found. Export from VEGAS Pro first."}

    success = import_timeline_from_json(str(json_path), log_fn=lambda msg: None)
    if success:
        return {"status": "success", "message": "VEGAS Pro timeline successfully synchronized to DaVinci Resolve Studio!"}
    else:
        return {"status": "error", "message": "Failed to sync to DaVinci Resolve. Ensure Resolve Studio is open."}


@mcp.tool()
def resolve_sync_to_vegas() -> Dict[str, Any]:
    """Export the active DaVinci Resolve timeline for import into VEGAS Pro."""
    bridge_dir = Path.home() / ".timeline_bridge"
    output_path = str(bridge_dir / "resolve_timeline.json")

    res = export_timeline_to_json(output_path, log_fn=lambda msg: None)
    if res and os.path.exists(res):
        return {
            "status": "success",
            "manifest_path": res,
            "message": "Resolve timeline exported. In VEGAS Pro, run 'Tools -> Scripting -> Receive from DaVinci Resolve'.",
        }
    else:
        return {"status": "error", "message": "Failed to export from DaVinci Resolve."}


@mcp.tool()
def resolve_get_project_info() -> Dict[str, Any]:
    """Get status and current active project/timeline from DaVinci Resolve Studio."""
    if not is_resolve_running():
        return {"status": "offline", "message": "DaVinci Resolve is not running or scripting is disabled."}

    info = get_current_project_info()
    if info:
        return {"status": "online", "project": info.get("project_name"), "timeline": info.get("timeline_name")}
    return {"status": "online", "message": "Connected to Resolve, but no project is open."}


if __name__ == "__main__":
    mcp.run()
