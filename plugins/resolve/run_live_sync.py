"""
run_live_sync.py — Background runner called by VEGAS Pro's SendToResolve.cs script.

Directly bridges VEGAS Pro timeline JSON into running DaVinci Resolve Studio.
"""

import sys
import os
from pathlib import Path

repo_dir = Path(r"C:\Users\Mi5a\VegasDavinciLinkTool")
if repo_dir.exists() and str(repo_dir) not in sys.path:
    sys.path.insert(0, str(repo_dir))

from core.live_bridge import import_timeline_from_json

def main():
    bridge_dir = Path.home() / ".timeline_bridge"
    json_path = bridge_dir / "vegas_timeline.json"

    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        json_path = Path(sys.argv[1])

    if not json_path.exists():
        print(f"[Error] Manifest not found: {json_path}")
        return

    success = import_timeline_from_json(str(json_path), log_fn=print)
    if not success:
        print("[Notice] Could not connect directly via background IPC.")
        print("[Notice] Please run 'Workspace > Scripts > ImportFromVegas' inside DaVinci Resolve,")
        print("[Notice] or import C:\\Users\\Mi5a\\.timeline_bridge\\Promo_Arrow_FinalCUTS.xml via File > Import > Timeline.")

if __name__ == "__main__":
    main()
