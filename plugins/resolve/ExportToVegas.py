"""
ExportToVegas.py — DaVinci Resolve Script Menu Integration.

Exports the active DaVinci Resolve timeline back to VEGAS Pro, enabling
bidirectional round-trip editing.

Place in:
  %APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Scripts\\Utility\\

Access via DaVinci Resolve:
  Workspace > Scripts > ExportToVegas
"""

import os
import sys
from pathlib import Path


def main():
    repo_dir = Path(r"C:\Users\Mi5a\VegasDavinciLinkTool")
    if repo_dir.exists() and str(repo_dir) not in sys.path:
        sys.path.insert(0, str(repo_dir))

    try:
        from core.live_bridge import export_timeline_to_json
        print("[ExportToVegas] Exporting active Resolve timeline...")
        out_path = export_timeline_to_json(log_fn=print)
        if out_path:
            print(f"[ExportToVegas] ✓ Successfully exported timeline to: {out_path}")
            print("[ExportToVegas] You can now click 'Receive from DaVinci Resolve' in VEGAS Pro!")
        else:
            print("[ExportToVegas] ✗ Export failed. Make sure a timeline is active.")
    except Exception as e:
        print(f"[ExportToVegas] Error: {e}")


if __name__ == "__main__":
    main()
