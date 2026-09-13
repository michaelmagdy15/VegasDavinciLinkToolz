"""
ExportToVegas.py — DaVinci Resolve Script Menu Integration.

Universal, multi-user compatible script exporting active DaVinci Resolve timeline back to VEGAS Pro.

Place in:
  %PROGRAMDATA%\\Blackmagic Design\\DaVinci Resolve\\Fusion\\Scripts\\Utility\\
  %APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Scripts\\Utility\\

Access via DaVinci Resolve:
  Workspace > Scripts > ExportToVegas
"""

import os
import sys
from pathlib import Path


def main():
    bridge_dir = Path.home() / ".timeline_bridge"
    if bridge_dir.exists() and str(bridge_dir) not in sys.path:
        sys.path.insert(0, str(bridge_dir))

    script_dir = Path(__file__).resolve().parent
    for candidate in [script_dir.parent.parent, Path.cwd()]:
        if (candidate / "core" / "live_bridge.py").exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))

    export_fn = None
    try:
        from core.live_bridge import export_timeline_to_json
        export_fn = export_timeline_to_json
    except ImportError:
        try:
            from live_bridge import export_timeline_to_json
            export_fn = export_timeline_to_json
        except ImportError as ie:
            print(f"[ExportToVegas] Could not import live_bridge module: {ie}")
            return

    try:
        print("[ExportToVegas] Exporting active Resolve timeline...")
        out_path = export_fn(log_fn=print)
        if out_path:
            print(f"[ExportToVegas] Successfully exported timeline to: {out_path}")
            print("[ExportToVegas] You can now click 'Receive from DaVinci Resolve' in VEGAS Pro!")
        else:
            print("[ExportToVegas] Export failed. Make sure a timeline is active.")
    except Exception as e:
        print(f"[ExportToVegas] Error: {e}")


if __name__ == "__main__":
    main()
