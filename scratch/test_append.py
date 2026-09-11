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
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()

print("Project:", proj.GetName())

# Read manifest
json_path = r"C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json"
with open(json_path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Find first clip in track 23
clip0 = data["tracks"][22]["clips"][0]
print("Testing clip:", clip0["name"], clip0["media_path"])
print("start_ms:", clip0["timeline_start_ms"], "len_ms:", clip0["timeline_length_ms"], "in_ms:", clip0["source_in_ms"])

# Find pool item
rf = mp.GetRootFolder()
pool_item = None
for f in rf.GetSubFolderList():
    for c in f.GetClipList():
        props = c.GetClipProperty()
        if props and props.get("File Path") and os.path.normpath(props["File Path"]).lower() == os.path.normpath(clip0["media_path"]).lower():
            pool_item = c
            break
    if pool_item:
        break

print("Found pool item:", pool_item.GetName() if pool_item else None)
if pool_item:
    props = pool_item.GetClipProperty()
    print("Clip Props:", {k: props[k] for k in ["Start TC", "End TC", "FPS", "Frames", "File Path"] if k in props})

# Get or create test timeline
tl_name = "Append_Test_TL"
tl = None
for i in range(1, proj.GetTimelineCount()+1):
    t = proj.GetTimelineByIndex(i)
    if t.GetName() == tl_name:
        tl = t
        break

if not tl:
    tl = mp.CreateEmptyTimeline(tl_name)

proj.SetCurrentTimeline(tl)
tl_start = tl.GetStartFrame()
print("Timeline StartFrame:", tl_start)

# Calculate frames
fps = 29.97
start_frame = int(round((float(clip0["timeline_start_ms"]) / 1000.0) * fps))
dur_frames = max(1, int(round((float(clip0["timeline_length_ms"]) / 1000.0) * fps)))
in_frame = int(round((float(clip0["source_in_ms"]) / 1000.0) * fps))
out_frame = in_frame + dur_frames
record_frame = tl_start + start_frame

print(f"in_frame: {in_frame}, out_frame: {out_frame}, record_frame: {record_frame}, dur_frames: {dur_frames}")

clip_info = {
    "mediaPoolItem": pool_item,
    "startFrame": in_frame,
    "endFrame": out_frame,
    "recordFrame": record_frame,
    "trackIndex": 1,
    "mediaType": 1,
}

print("Calling AppendToTimeline with:", clip_info)
res = mp.AppendToTimeline([clip_info])
print("AppendToTimeline result:", res)
items = tl.GetItemListInTrack("video", 1) or []
print("Items in V1:", len(items))
for it in items:
    print("  Item:", it.GetName(), "Start:", it.GetStart(), "End:", it.GetEnd())
