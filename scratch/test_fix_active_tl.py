import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print(f"Timeline: {tl.GetName()}")

# 1. Inspect and fix film burn clip
for track_idx in range(1, tl.GetTrackCount("video") + 1):
    items = tl.GetItemListInTrack("video", track_idx) or []
    for it in items:
        name = it.GetName().lower()
        if "filmburn" in name:
            print(f"Fixing filmburn on Video Track {track_idx}:")
            it.SetProperty("CompositeMode", 5)  # Screen mode
            it.SetProperty("Pan", 0.0)
            it.SetProperty("Tilt", 0.0)
            it.SetProperty("ZoomX", 1.0)
            it.SetProperty("ZoomY", 1.0)
            it.SetProperty("Scaling", 3)  # Fill full frame
            print("  Filmburn updated:", {k: it.GetProperty(k) for k in ["CompositeMode", "Pan", "Tilt", "ZoomX", "ZoomY", "Scaling"]})

# 2. Fix all video clips that had bad 540, 960 offsets
fixed_count = 0
for track_idx in range(1, tl.GetTrackCount("video") + 1):
    items = tl.GetItemListInTrack("video", track_idx) or []
    for it in items:
        pan = it.GetProperty("Pan")
        tilt = it.GetProperty("Tilt")
        zx = it.GetProperty("ZoomX")
        # If it was shifted by our buggy 540, 960 formula:
        if abs(pan - 540.0) < 1.0 and abs(tilt - 960.0) < 1.0:
            it.SetProperty("Pan", 0.0)
            it.SetProperty("Tilt", 0.0)
            it.SetProperty("ZoomX", 1.0)
            it.SetProperty("ZoomY", 1.0)
            it.SetProperty("Scaling", 3)  # Fill 1080x1920 vertical
            fixed_count += 1

print(f"Reset {fixed_count} clips with buggy Pan=540/Tilt=960 to centered Fill!")
