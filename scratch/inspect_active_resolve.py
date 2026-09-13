import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()

print(f"Project: {proj.GetName()}")
print(f"Timeline: {tl.GetName()}")
print(f"Video tracks: {tl.GetTrackCount('video')}")
print(f"Audio tracks: {tl.GetTrackCount('audio')}")

# Inspect Video Tracks
print("\n=== VIDEO TRACKS IN RESOLVE ===")
for i in range(1, tl.GetTrackCount("video") + 1):
    name = tl.GetTrackName("video", i)
    items = tl.GetItemListInTrack("video", i) or []
    if len(items) > 0 or "burn" in name.lower() or i in (3, 4, 9, 27, 28):
        print(f"V{i} '{name}': {len(items)} items")
        if i == 3 or "burn" in name.lower():
            for item in items[:3]:
                print(f"   Item: {item.GetName()}")
                for p in ["CompositeMode", "Opacity", "Pan", "Tilt", "ZoomX", "ZoomY", "Scaling"]:
                    print(f"      {p} = {item.GetProperty(p)}")

# Inspect Audio Tracks
print("\n=== AUDIO TRACKS IN RESOLVE ===")
for i in range(1, min(tl.GetTrackCount("audio") + 1, 25)):
    name = tl.GetTrackName("audio", i)
    items = tl.GetItemListInTrack("audio", i) or []
    if len(items) > 0:
        print(f"A{i} '{name}': {len(items)} items")
        first = items[0]
        # Check what properties audio items have
        keys = ["Volume", "Pan", "Gain", "FadeIn", "FadeOut"]
        props = {}
        for k in keys:
            v = first.GetProperty(k)
            if v is not None:
                props[k] = v
        print(f"      Props: {props}")
