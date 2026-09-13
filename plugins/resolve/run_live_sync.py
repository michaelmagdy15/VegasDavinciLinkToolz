"""
run_live_sync.py — Background runner called by VEGAS Pro's SendToResolve.cs script.

Directly bridges VEGAS Pro timeline JSON into running DaVinci Resolve Studio.
Universal and multi-user compatible.
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

    import_fn = None
    try:
        from core.live_bridge import import_timeline_from_json
        import_fn = import_timeline_from_json
    except ImportError:
        try:
            from live_bridge import import_timeline_from_json
            import_fn = import_timeline_from_json
        except ImportError as ie:
            print(f"[Error] Could not import live_bridge: {ie}")
            return

    json_path = bridge_dir / "vegas_timeline.json"
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        json_path = Path(sys.argv[1])

    if not json_path.exists():
        print(f"[Error] Manifest not found: {json_path}")
        return

    success = import_fn(str(json_path), log_fn=print)
    if not success:
        print("[Notice] Could not connect directly via background IPC.")
        print("[Notice] Please run 'Workspace > Scripts > ImportFromVegas' inside DaVinci Resolve.")


if __name__ == "__main__":
    main()
