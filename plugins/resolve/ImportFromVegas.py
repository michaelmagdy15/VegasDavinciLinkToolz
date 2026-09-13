"""
ImportFromVegas.py — DaVinci Resolve Script Menu Integration.

Universal, multi-user compatible script connecting to VEGAS Pro Live Link.

Place in:
  %PROGRAMDATA%\\Blackmagic Design\\DaVinci Resolve\\Fusion\\Scripts\\Utility\\
  %APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Scripts\\Utility\\

Access via DaVinci Resolve:
  Workspace > Scripts > ImportFromVegas
"""

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

    # Pass resolve reference to __main__ if defined by DaVinci Resolve script host
    try:
        import __main__
        if "resolve" in globals() and not hasattr(__main__, "resolve"):
            __main__.resolve = globals()["resolve"]
        if "bmd" in globals() and not hasattr(__main__, "bmd"):
            __main__.bmd = globals()["bmd"]
    except Exception:
        pass

    # Ensure ~/.timeline_bridge and current script repo are on sys.path
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
            print(f"[ImportFromVegas] Could not import live_bridge module: {ie}")
            return

    try:
        print(f"[ImportFromVegas] Loading manifest: {json_path}")
        success = import_fn(str(json_path), log_fn=print)
        if success:
            print("[ImportFromVegas] Successfully synced timeline from VEGAS Pro!")
        else:
            print("[ImportFromVegas] Failed to sync timeline.")
    except Exception as e:
        print(f"[ImportFromVegas] Error: {e}")


if __name__ == "__main__":
    main()
