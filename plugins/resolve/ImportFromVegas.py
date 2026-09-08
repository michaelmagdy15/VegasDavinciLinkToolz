"""
ImportFromVegas.py — DaVinci Resolve Script Menu Integration.

Place in:
  %APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Scripts\\Utility\\

Access via DaVinci Resolve:
  Workspace > Scripts > ImportFromVegas
"""

import json
import os
import sys
from pathlib import Path


def main():
    bridge_dir = Path.home() / ".timeline_bridge"
    json_path = bridge_dir / "vegas_timeline.json"

    if not json_path.exists():
        print(f"[ImportFromVegas] No timeline manifest found at: {json_path}")
        print("[ImportFromVegas] Please click 'Send to DaVinci Resolve' in VEGAS Pro first.")
        return

    # Try to find core live_bridge
    repo_dir = Path(r"C:\Users\Mi5a\VegasDavinciLinkTool")
    if repo_dir.exists() and str(repo_dir) not in sys.path:
        sys.path.insert(0, str(repo_dir))

    try:
        from core.live_bridge import import_timeline_from_json
        print(f"[ImportFromVegas] Loading manifest: {json_path}")
        success = import_timeline_from_json(str(json_path), log_fn=print)
        if success:
            print("[ImportFromVegas] ✓ Successfully synced timeline from VEGAS Pro!")
        else:
            print("[ImportFromVegas] ✗ Failed to sync timeline.")
    except Exception as e:
        print(f"[ImportFromVegas] Error: {e}")


if __name__ == "__main__":
    main()
