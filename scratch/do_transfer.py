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
if not proj:
    print("[ERROR] No project open in DaVinci Resolve!")
    sys.exit(1)

print(f"[OK] Connected to DaVinci Resolve. Active Project: '{proj.GetName()}'")
mp = proj.GetMediaPool()
rf = mp.GetRootFolder()

# 1. Clean up duplicate clips in 'VEGAS Live Import'
vfolder = None
for f in rf.GetSubFolderList():
    if f.GetName() == "VEGAS Live Import":
        vfolder = f
        break

if vfolder:
    clips = vfolder.GetClipList()
    seen = set()
    to_delete = []
    for c in clips:
        p = ""
        try:
            props = c.GetClipProperty()
            if props:
                p = props.get("File Path", "")
        except Exception:
            pass
        key = os.path.normpath(p).lower() if p else c.GetName()
        if key in seen:
            to_delete.append(c)
        else:
            seen.add(key)
    if to_delete:
        print(f"[INFO] Removing {len(to_delete)} duplicate clips from 'VEGAS Live Import' bin...")
        # Delete in batches of 50 to avoid any IPC limits
        for i in range(0, len(to_delete), 50):
            mp.DeleteClips(to_delete[i:i+50])
        print(f"[OK] 'VEGAS Live Import' now has {len(vfolder.GetClipList())} unique clips.")

# 2. Delete empty failed sync timelines from earlier
timelines_to_delete = []
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t and "Promo Arrow FinalCUTS (VEGAS Sync)" in t.GetName():
        v1_items = t.GetItemListInTrack("video", 1) or []
        if len(v1_items) <= 1:
            timelines_to_delete.append(t)

if timelines_to_delete:
    print(f"[INFO] Deleting {len(timelines_to_delete)} empty/failed sync timelines: {[t.GetName() for t in timelines_to_delete]}")
    mp.DeleteTimelines(timelines_to_delete)

# 3. Read manifest
json_path = r"C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json"
with open(json_path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

project_name = data.get("project_name", "Promo Arrow FinalCUTS")
fps = float(data.get("frame_rate", 29.97))
tracks = data.get("tracks", [])

# 4. Build map of all media pool items
clip_map = {}
def collect_clips(folder):
    for c in folder.GetClipList():
        cname = c.GetName()
        clip_map[cname] = c
        clip_map[Path(cname).stem] = c
        try:
            props = c.GetClipProperty()
            if props and "File Path" in props and props["File Path"]:
                clip_map[os.path.normpath(props["File Path"]).lower()] = c
        except Exception:
            pass
    for sub in folder.GetSubFolderList():
        collect_clips(sub)

collect_clips(rf)
print(f"[INFO] Indexed {len(clip_map)} media pool references.")

# 5. Check missing files and import if necessary
missing_paths = set()
for track in tracks:
    for clip in track.get("clips", []):
        mpath = clip.get("media_path", "")
        if mpath and os.path.isfile(mpath):
            norm_p = os.path.normpath(mpath).lower()
            fname = Path(mpath).name
            if norm_p not in clip_map and fname not in clip_map and Path(mpath).stem not in clip_map:
                missing_paths.add(mpath)

if missing_paths:
    print(f"[INFO] Importing {len(missing_paths)} missing media files into 'VEGAS Live Import'...")
    if not vfolder:
        vfolder = mp.AddSubFolder(rf, "VEGAS Live Import")
    mp.SetCurrentFolder(vfolder)
    mp.ImportMedia(list(missing_paths))
    collect_clips(vfolder)

# 6. Create clean new sync timeline
timeline_name = f"{project_name} (VEGAS Cuts)"
existing_names = set(proj.GetTimelineByIndex(i).GetName() for i in range(1, proj.GetTimelineCount() + 1))
ver = 2
base_name = timeline_name
while timeline_name in existing_names:
    timeline_name = f"{base_name} {ver}"
    ver += 1

print(f"[INFO] Creating timeline: '{timeline_name}'...")
timeline = mp.CreateEmptyTimeline(timeline_name)
if not timeline:
    print(f"[ERROR] Could not create timeline '{timeline_name}'")
    sys.exit(1)

proj.SetCurrentTimeline(timeline)
tl_start = timeline.GetStartFrame() or 0
print(f"[OK] Created timeline: '{timeline_name}' (StartFrame: {tl_start})")

# Separate video and audio tracks with independent 1-based indexing
track_map = {}
v_idx = 1
a_idx = 1
for t in tracks:
    if t.get("is_video", True):
        track_map[id(t)] = (1, v_idx, t.get("name", f"Video {v_idx}"))
        v_idx += 1
    else:
        track_map[id(t)] = (2, a_idx, t.get("name", f"Audio {a_idx}"))
        a_idx += 1

total_v = v_idx - 1
total_a = a_idx - 1
print(f"[INFO] Target layout: {total_v} Video Tracks, {total_a} Audio Tracks")

# Ensure sufficient tracks
curr_v = timeline.GetTrackCount("video")
while curr_v < total_v:
    if timeline.AddTrack("video"):
        curr_v += 1
    else:
        break

curr_a = timeline.GetTrackCount("audio")
while curr_a < total_a:
    if timeline.AddTrack("audio", "stereo"):
        curr_a += 1
    else:
        break

# Rename tracks
for t in tracks:
    tinfo = track_map.get(id(t))
    if tinfo:
        mtype, tidx, tname = tinfo
        ttype_str = "video" if mtype == 1 else "audio"
        if tname and tidx <= timeline.GetTrackCount(ttype_str):
            try:
                timeline.SetTrackName(ttype_str, tidx, tname)
            except Exception:
                pass

# 7. Append all clips
clips_added = 0
clips_skipped = 0

for track in tracks:
    tinfo = track_map.get(id(track))
    if not tinfo:
        continue
    media_type, target_track_idx, track_name = tinfo
    is_video = (media_type == 1)

    for clip in track.get("clips", []):
        mpath = clip.get("media_path", "")
        if not mpath:
            continue

        fname = Path(mpath).name
        pool_item = (
            clip_map.get(os.path.normpath(mpath).lower()) or
            clip_map.get(fname) or
            clip_map.get(Path(mpath).stem)
        )

        if not pool_item and os.path.isfile(mpath):
            try:
                imp = mp.ImportMedia([mpath])
                if imp and len(imp) > 0:
                    pool_item = imp[0]
                    clip_map[fname] = pool_item
            except Exception:
                pass

        if not pool_item:
            clips_skipped += 1
            continue

        start_ms = float(clip.get("timeline_start_ms", 0.0))
        len_ms = float(clip.get("timeline_length_ms", 0.0))
        in_ms = float(clip.get("source_in_ms", 0.0))

        clip_fps = fps
        try:
            clip_props = pool_item.GetClipProperty()
            if clip_props:
                for key in ["FPS", "Frame Rate", "Video Frame Rate"]:
                    if key in clip_props and clip_props[key]:
                        raw_val = str(clip_props[key]).split()[0]
                        fps_val = float(raw_val)
                        if fps_val > 0:
                            clip_fps = fps_val
                            break
        except Exception:
            clip_fps = fps

        playback_rate = float(clip.get("playback_rate", 1.0))
        if playback_rate <= 0:
            playback_rate = 1.0

        in_frame = int(round((in_ms / 1000.0) * clip_fps))
        dur_src = int(round((len_ms / 1000.0) * clip_fps * playback_rate))
        out_frame = in_frame + max(1, dur_src)

        start_frame = int(round((start_ms / 1000.0) * fps))
        record_frame = tl_start + start_frame

        clip_info = {
            "mediaPoolItem": pool_item,
            "startFrame": in_frame,
            "endFrame": out_frame,
            "recordFrame": record_frame,
            "trackIndex": target_track_idx,
            "mediaType": media_type,
        }

        try:
            res = mp.AppendToTimeline([clip_info])
            if res:
                clips_added += 1
                if is_video and len(res) > 0:
                    item = res[0]
                    rot = clip.get("rotation_angle", 0.0)
                    zx = clip.get("zoom_x", 1.0)
                    zy = clip.get("zoom_y", 1.0)
                    px = clip.get("pan_x", 0.0)
                    py = clip.get("pan_y", 0.0)
                    try:
                        if abs(rot) > 0.01:
                            item.SetProperty("RotationAngle", float(rot))
                        if abs(zx - 1.0) > 0.001:
                            item.SetProperty("ZoomX", float(zx))
                        if abs(zy - 1.0) > 0.001:
                            item.SetProperty("ZoomY", float(zy))
                        if abs(px) > 0.01:
                            item.SetProperty("Pan", float(px))
                        if abs(py) > 0.01:
                            item.SetProperty("Tilt", float(py))
                    except Exception:
                        pass
            else:
                clips_skipped += 1
        except Exception as e:
            clips_skipped += 1

    # Mute state
    if track.get("mute", False):
        try:
            ttype = "video" if is_video else "audio"
            timeline.SetTrackEnable(ttype, target_track_idx, False)
        except Exception:
            pass

print(f"[OK] Transfer Complete: {clips_added} cuts placed on timeline (Skipped: {clips_skipped})")

# 8. Add Markers & Regions
markers_added = 0
for m in data.get("markers", []):
    lbl = m.get("label", "VEGAS Marker")
    pos_ms = m.get("position_ms", 0.0)
    mf = tl_start + int(round((pos_ms / 1000.0) * fps))
    try:
        if timeline.AddMarker(mf, "Cyan", lbl, "", 1):
            markers_added += 1
    except Exception:
        pass

for r in data.get("regions", []):
    lbl = r.get("label", "VEGAS Region")
    pos_ms = r.get("position_ms", 0.0)
    len_ms = r.get("length_ms", 0.0)
    sf = tl_start + int(round((pos_ms / 1000.0) * fps))
    df = max(1, int(round((len_ms / 1000.0) * fps)))
    try:
        if timeline.AddMarker(sf, "Yellow", lbl, "", df):
            markers_added += 1
    except Exception:
        pass

if markers_added > 0:
    print(f"[OK] Synced {markers_added} timeline markers/regions.")
