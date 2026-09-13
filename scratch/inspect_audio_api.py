import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()

print("=== PROJECT METHODS ===")
for m in dir(proj):
    if any(k in m.lower() for k in ["fairlight", "preset", "audio", "track"]):
        print(f"  proj.{m}")

print("\n=== TIMELINE METHODS ===")
for m in dir(tl):
    if any(k in m.lower() for k in ["fairlight", "preset", "audio", "track", "volume", "fade", "transition"]):
        print(f"  tl.{m}")

print("\n=== TIMELINE SETTING KEYS ===")
try:
    for k in ["timelineResolutionWidth", "timelineResolutionHeight", "timelineFrameRate", "audioTrackCount", "fairlightPreset"]:
        v = tl.GetSetting(k)
        print(f"  {k} = {v}")
except Exception as e:
    print(f"  GetSetting error: {e}")

# Check Fairlight Presets
try:
    presets = proj.GetFairlightPresets()
    print(f"\nFairlight Presets in Project: {presets}")
except Exception as e:
    print(f"GetFairlightPresets error: {e}")
