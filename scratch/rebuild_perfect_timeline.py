import sys
import os
import json
from pathlib import Path

# Force UTF-8 encoding on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Setup Resolve scripting paths
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
if not resolve:
    print("[ERROR] Could not connect to DaVinci Resolve!")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
rf = mp.GetRootFolder()

# 1. Clean existing sync timelines so we have a fresh, pristine timeline
to_del = []
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t and "Promo Arrow FinalCUTS (VEGAS Cuts)" in t.GetName():
        to_del.append(t)

if to_del:
    print(f"[INFO] Removing previous test timelines: {[t.GetName() for t in to_del]}")
    mp.DeleteTimelines(to_del)

# 2. Read and sanitize manifest
json_path = r"C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json"
with open(json_path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Ensure film burn has Screen composite mode
for t in data["tracks"]:
    tname = t.get("name", "").lower()
    if "burn" in tname or "screen" in tname:
        t["composite_mode"] = "Screen"
    elif "lut" in tname:
        t["is_adjustment"] = True

    # Sanitize buggy pan/crop calculations:
    for c in t.get("clips", []):
        px = float(c.get("pan_x", 0.0))
        py = float(c.get("pan_y", 0.0))
        zx = float(c.get("zoom_x", 1.0))
        # Reset Sony A7IV default offset (540, 960, 0.5)
        if abs(px - 540.0) < 1.0 and abs(py - 960.0) < 1.0:
            c["pan_x"] = 0.0
            c["pan_y"] = 0.0
            c["zoom_x"] = 1.0
            c["zoom_y"] = 1.0
        # Reset DJI Drone default offset (1380, 120, 0.8889)
        elif abs(px - 1380.0) < 1.0 and abs(py - 120.0) < 1.0:
            c["pan_x"] = 0.0
            c["pan_y"] = 0.0
            c["zoom_x"] = 1.0
            c["zoom_y"] = 1.0
        # For filmburn, reset pan/tilt so it overlays full screen
        elif "filmburn" in c.get("name", "").lower():
            c["pan_x"] = 0.0
            c["pan_y"] = 0.0
            c["zoom_x"] = 1.0
            c["zoom_y"] = 1.0

# Save sanitized manifest
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("[OK] Manifest sanitized with Screen composite mode, centered framing, and adjustment flags.")

# 3. Call live_bridge to build the timeline
repo_dir = Path(r"C:\Users\Mi5a\VegasDavinciLinkTool")
if str(repo_dir) not in sys.path:
    sys.path.insert(0, str(repo_dir))

from core.live_bridge import import_timeline_from_json

success = import_timeline_from_json(json_path, log_fn=print)
if success:
    print("\n[SUCCESS] Timeline built with full track hierarchy, Screen blending, and 1080x1920 Fill scaling!")
else:
    print("\n[FAILED] Timeline import failed.")
