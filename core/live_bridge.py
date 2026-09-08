"""
live_bridge.py — Direct live synchronization between VEGAS Pro and DaVinci Resolve.

Bypasses manual file export / import dialogs by using the official
DaVinci Resolve Python API (DaVinciResolveScript) to connect directly
to a running DaVinci Resolve Studio instance.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote


def xml_to_timeline_json(xml_path: str, json_path: Optional[str] = None) -> str:
    """Convert an existing VEGAS XML file into the universal timeline JSON manifest."""
    import xml.etree.ElementTree as ET

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Collect master file definitions
    file_map = {}
    for f in root.findall(".//file"):
        fid = f.get("id")
        purl = f.find("pathurl")
        if fid and purl is not None and purl.text:
            raw = purl.text.replace("file://localhost/", "")
            file_map[fid] = unquote(raw).replace("/", "\\")

    seq = root.find(".//sequence")
    if seq is None:
        raise ValueError("No <sequence> found in XML.")

    name = seq.find("name").text if seq.find("name") is not None else "Timeline"
    rate_elem = seq.find("rate")
    tb = 30.0
    if rate_elem is not None:
        tb_elem = rate_elem.find("timebase")
        if tb_elem is not None:
            tb = float(tb_elem.text)
        ntsc_elem = rate_elem.find("ntsc")
        if ntsc_elem is not None and ntsc_elem.text.upper() == "TRUE":
            tb = 29.97

    tracks = []
    media = seq.find("media")
    if media is not None:
        v = media.find("video")
        if v is not None:
            for idx, track in enumerate(v.findall("track")):
                clips = []
                for item in track.findall("clipitem"):
                    cname = item.find("name").text if item.find("name") is not None else ""
                    mpath = ""
                    purl = item.find(".//pathurl")
                    if purl is not None and purl.text:
                        raw = purl.text.replace("file://localhost/", "")
                        mpath = unquote(raw).replace("/", "\\")
                    else:
                        file_elem = item.find("file")
                        if file_elem is not None:
                            fid = file_elem.get("id")
                            mpath = file_map.get(fid, "")

                    start_f = float(item.find("start").text) if item.find("start") is not None else 0.0
                    end_f = float(item.find("end").text) if item.find("end") is not None else 0.0
                    in_f = float(item.find("in").text) if item.find("in") is not None else 0.0
                    dur_f = max(0.0, end_f - start_f)

                    start_ms = (start_f / tb) * 1000.0
                    len_ms = (dur_f / tb) * 1000.0
                    in_ms = (in_f / tb) * 1000.0

                    clips.append({
                        "name": cname,
                        "media_path": mpath,
                        "timeline_start_ms": start_ms,
                        "timeline_length_ms": len_ms,
                        "source_in_ms": in_ms,
                    })
                tracks.append({
                    "name": f"Video {idx + 1}",
                    "index": idx,
                    "is_video": True,
                    "is_audio": False,
                    "clips": clips,
                })

        a = media.find("audio")
        if a is not None:
            for idx, track in enumerate(a.findall("track")):
                clips = []
                for item in track.findall("clipitem"):
                    cname = item.find("name").text if item.find("name") is not None else ""
                    mpath = ""
                    purl = item.find(".//pathurl")
                    if purl is not None and purl.text:
                        raw = purl.text.replace("file://localhost/", "")
                        mpath = unquote(raw).replace("/", "\\")
                    else:
                        file_elem = item.find("file")
                        if file_elem is not None:
                            fid = file_elem.get("id")
                            mpath = file_map.get(fid, "")

                    start_f = float(item.find("start").text) if item.find("start") is not None else 0.0
                    end_f = float(item.find("end").text) if item.find("end") is not None else 0.0
                    in_f = float(item.find("in").text) if item.find("in") is not None else 0.0
                    dur_f = max(0.0, end_f - start_f)

                    start_ms = (start_f / tb) * 1000.0
                    len_ms = (dur_f / tb) * 1000.0
                    in_ms = (in_f / tb) * 1000.0

                    clips.append({
                        "name": cname,
                        "media_path": mpath,
                        "timeline_start_ms": start_ms,
                        "timeline_length_ms": len_ms,
                        "source_in_ms": in_ms,
                    })
                tracks.append({
                    "name": f"Audio {idx + 1}",
                    "index": idx,
                    "is_video": False,
                    "is_audio": True,
                    "clips": clips,
                })

    data = {
        "project_name": name,
        "frame_rate": tb,
        "width": 1920,
        "height": 1080,
        "tracks": tracks,
    }

    if not json_path:
        bridge_dir = Path.home() / ".timeline_bridge"
        bridge_dir.mkdir(parents=True, exist_ok=True)
        json_path = str(bridge_dir / "vegas_timeline.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return json_path


def _init_resolve_env() -> None:
    """Ensure DaVinci Resolve scripting environment variables and paths are set."""
    if sys.platform == "win32":
        default_lib = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        default_mod = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
        
        if "RESOLVE_SCRIPT_LIB" not in os.environ and os.path.exists(default_lib):
            os.environ["RESOLVE_SCRIPT_LIB"] = default_lib
        if "PYTHONPATH" not in os.environ and os.path.exists(default_mod):
            os.environ["PYTHONPATH"] = default_mod
        if default_mod not in sys.path and os.path.exists(default_mod):
            sys.path.append(default_mod)


def get_resolve_app():
    """Connect to the currently running DaVinci Resolve instance.

    Returns:
        resolve object if connected, None otherwise.
    """
    _init_resolve_env()
    try:
        import DaVinciResolveScript as dvr
        return dvr.scriptapp("Resolve")
    except Exception:
        return None


def is_resolve_running() -> bool:
    """Check if DaVinci Resolve is currently running and responding to scripting."""
    app = get_resolve_app()
    return app is not None


def get_current_project_info() -> Optional[Dict[str, str]]:
    """Return summary of current open project and timeline in Resolve."""
    resolve = get_resolve_app()
    if not resolve:
        return None

    pm = resolve.GetProjectManager()
    if not pm:
        return None

    proj = pm.GetCurrentProject()
    if not proj:
        return None

    tl = proj.GetCurrentTimeline()
    return {
        "project_name": proj.GetName(),
        "timeline_name": tl.GetName() if tl else "None",
    }


def align_media_pool_timecodes(folder=None, target_timecode: str = "00:00:00:00") -> int:
    """Set the Start TC of clips in a Media Pool folder to 00:00:00:00.

    This resolves the 'timecode extents do not match' error when conforming
    VEGAS Pro timelines, which are 0-based.

    Returns:
        Number of clips whose Start TC was updated.
    """
    resolve = get_resolve_app()
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve. Is Resolve running?")

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        raise RuntimeError("No project is currently open in DaVinci Resolve.")

    mp = proj.GetMediaPool()
    updated_count = 0
    target_folder = folder if folder is not None else mp.GetRootFolder()

    def walk_and_fix(f):
        nonlocal updated_count
        for clip in f.GetClipList():
            props = clip.GetClipProperty()
            if props:
                try:
                    if clip.SetClipProperty("Start TC", target_timecode):
                        updated_count += 1
                except Exception:
                    pass
        for sub in f.GetSubFolderList():
            walk_and_fix(sub)

    walk_and_fix(target_folder)
    return updated_count


def import_timeline_from_json(json_path: str, log_fn=print) -> bool:
    """Build a timeline directly inside DaVinci Resolve from a VEGAS JSON manifest.

    Args:
        json_path: Path to the vegas_timeline.json manifest.
        log_fn: Logging callback function.

    Returns:
        True if timeline was created and populated successfully, False otherwise.
    """
    if not os.path.isfile(json_path):
        log_fn(f"[ERROR] Manifest file not found: {json_path}")
        return False

    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    resolve = get_resolve_app()
    if not resolve:
        log_fn("[ERROR] Could not connect to DaVinci Resolve. Please launch Resolve.")
        return False

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        log_fn("[ERROR] No project is currently open in DaVinci Resolve.")
        return False

    mp = proj.GetMediaPool()
    root_folder = mp.GetRootFolder()

    project_name = data.get("project_name", "VEGAS Live Sync")
    fps = data.get("frame_rate", 29.97)
    tracks = data.get("tracks", [])

    log_fn(f"[INFO] Connecting to project: '{proj.GetName()}'")
    log_fn(f"[INFO] Syncing timeline: '{project_name}' ({fps:.2f} fps)")

    # 1. Collect all unique media paths to import
    media_paths = set()
    for track in tracks:
        for clip in track.get("clips", []):
            mpath = clip.get("media_path", "")
            if mpath and os.path.isfile(mpath):
                media_paths.add(mpath)

    # 2. Ingest media into a dedicated Media Pool subfolder
    sub_folder = None
    for f in root_folder.GetSubFolderList():
        if f.GetName() == "VEGAS Live Import":
            sub_folder = f
            break
    if not sub_folder:
        sub_folder = mp.AddSubFolder(root_folder, "VEGAS Live Import")

    mp.SetCurrentFolder(sub_folder)

    if media_paths:
        log_fn(f"[INFO] Importing {len(media_paths)} media files into Media Pool...")
        mp.ImportMedia(list(media_paths))

    # 3. Reset Start TC to 00:00:00:00 for imported clips to ensure 100% conform alignment
    log_fn("[INFO] Aligning clip timecodes to 00:00:00:00...")
    align_media_pool_timecodes(folder=sub_folder, target_timecode="00:00:00:00")

    # Map filename to MediaPoolItem across all Media Pool folders
    clip_map = {}
    def collect_clips(folder):
        for c in folder.GetClipList():
            clip_map[c.GetName()] = c
        for sub in folder.GetSubFolderList():
            collect_clips(sub)

    collect_clips(root_folder)
    # Ensure VEGAS Live Import clips take highest precedence
    for c in sub_folder.GetClipList():
        clip_map[c.GetName()] = c

    log_fn(f"[INFO] Media Pool items available: {len(clip_map)}")

    # 4. Create timeline (auto-increment version so repeated syncs never conflict)
    base_name = f"{project_name} (VEGAS Sync)"
    existing_names = set()
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if t:
            existing_names.add(t.GetName())

    timeline_name = base_name
    version = 2
    while timeline_name in existing_names:
        timeline_name = f"{base_name} {version}"
        version += 1

    timeline = mp.CreateEmptyTimeline(timeline_name)
    if not timeline:
        log_fn(f"[ERROR] Failed to create timeline '{timeline_name}' in Resolve.")
        return False

    proj.SetCurrentTimeline(timeline)
    tl_start = timeline.GetStartFrame() or 0
    log_fn(f"[OK] Created timeline: '{timeline_name}' (StartFrame: {tl_start})")

    # 5. Build clips into timeline
    clips_added = 0
    for track in tracks:
        is_video = track.get("is_video", True)
        track_idx = track.get("index", 0) + 1  # 1-based index in Resolve

        for clip in track.get("clips", []):
            mpath = clip.get("media_path", "")
            if not mpath:
                continue

            fname = Path(mpath).name
            pool_item = clip_map.get(fname)
            if not pool_item:
                continue

            start_ms = clip.get("timeline_start_ms", 0.0)
            len_ms = clip.get("timeline_length_ms", 0.0)
            # Determine source clip frame rate for accurate source in/out calculation
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

            # Check playback rate (speed/retime)
            playback_rate = clip.get("playback_rate", 1.0)
            if playback_rate <= 0:
                playback_rate = 1.0

            # Source frames in/out must use the source clip's native FPS scaled by playback rate
            in_frame = int(round((in_ms / 1000.0) * clip_fps))
            duration_src_frames = int(round((len_ms / 1000.0) * clip_fps * playback_rate))
            out_frame = in_frame + duration_src_frames

            # Timeline recordFrame uses sequence FPS and timeline StartFrame offset
            start_frame = int(round((start_ms / 1000.0) * fps))
            record_frame = tl_start + start_frame

            clip_info = {
                "mediaPoolItem": pool_item,
                "startFrame": in_frame,
                "endFrame": out_frame,
                "recordFrame": record_frame,
                "trackIndex": track_idx,
                "mediaType": 1 if is_video else 2,
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
            except Exception:
                pass

        # Apply track mute state
        if track.get("mute", False):
            try:
                track_type = "video" if is_video else "audio"
                timeline.SetTrackEnable(track_type, track_idx, False)
            except Exception:
                pass

    # 6. Inject Timeline Markers & Regions
    markers_added = 0
    for m in data.get("markers", []):
        lbl = m.get("label", "VEGAS Marker")
        pos_ms = m.get("position_ms", 0.0)
        marker_frame = tl_start + int(round((pos_ms / 1000.0) * fps))
        try:
            if timeline.AddMarker(marker_frame, "Cyan", lbl, "", 1):
                markers_added += 1
        except Exception:
            pass

    for r in data.get("regions", []):
        lbl = r.get("label", "VEGAS Region")
        pos_ms = r.get("position_ms", 0.0)
        len_ms = r.get("length_ms", 0.0)
        start_frame = tl_start + int(round((pos_ms / 1000.0) * fps))
        dur_frames = max(1, int(round((len_ms / 1000.0) * fps)))
        try:
            if timeline.AddMarker(start_frame, "Yellow", lbl, "", dur_frames):
                markers_added += 1
        except Exception:
            pass

    if markers_added > 0:
        log_fn(f"[OK] Synced {markers_added} timeline markers and regions!")

    log_fn(f"[OK] Timeline built with {clips_added} cuts synchronized live (zero gap aligned)!")
    return True


def export_timeline_to_json(output_json_path: Optional[str] = None, log_fn=print) -> Optional[str]:
    """Export the active DaVinci Resolve timeline to universal JSON for VEGAS Pro.

    Enables two-way round-trip synchronization between Resolve and VEGAS Pro.
    """
    resolve = get_resolve_app()
    if not resolve:
        log_fn("[ERROR] Could not connect to DaVinci Resolve.")
        return None

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        log_fn("[ERROR] No project currently open in DaVinci Resolve.")
        return None

    timeline = proj.GetCurrentTimeline()
    if not timeline:
        log_fn("[ERROR] No timeline currently active in DaVinci Resolve.")
        return None

    tl_name = timeline.GetName()
    tl_start = timeline.GetStartFrame() or 0
    fps_setting = timeline.GetSetting("timelineFrameRate")
    try:
        fps = float(fps_setting) if fps_setting else 29.97
    except ValueError:
        fps = 29.97

    log_fn(f"[INFO] Exporting active Resolve timeline '{tl_name}' ({fps:.2f} fps)...")

    tracks = []
    # Video tracks
    v_track_count = timeline.GetTrackCount("video")
    for t_idx in range(1, v_track_count + 1):
        items = timeline.GetItemListInTrack("video", t_idx)
        clips = []
        for it in items:
            mp_item = it.GetMediaPoolItem()
            mpath = mp_item.GetClipProperty("File Path") if mp_item else ""
            clip_fps = fps
            if mp_item:
                try:
                    c_props = mp_item.GetClipProperty()
                    if c_props and "FPS" in c_props:
                        clip_fps = float(c_props["FPS"])
                except Exception:
                    clip_fps = fps

            start_f = it.GetStart() - tl_start
            dur_f = it.GetDuration()
            left_offset = it.GetLeftOffset() or 0

            clips.append({
                "name": it.GetName(),
                "media_path": mpath,
                "timeline_start_ms": (start_f / fps) * 1000.0,
                "timeline_length_ms": (dur_f / fps) * 1000.0,
                "source_in_ms": (left_offset / clip_fps) * 1000.0,
            })

        tracks.append({
            "name": timeline.GetTrackName("video", t_idx) or f"Video {t_idx}",
            "index": t_idx - 1,
            "is_video": True,
            "is_audio": False,
            "clips": clips,
        })

    # Audio tracks
    a_track_count = timeline.GetTrackCount("audio")
    for t_idx in range(1, a_track_count + 1):
        items = timeline.GetItemListInTrack("audio", t_idx)
        clips = []
        for it in items:
            mp_item = it.GetMediaPoolItem()
            mpath = mp_item.GetClipProperty("File Path") if mp_item else ""

            start_f = it.GetStart() - tl_start
            dur_f = it.GetDuration()
            left_offset = it.GetLeftOffset() or 0

            clips.append({
                "name": it.GetName(),
                "media_path": mpath,
                "timeline_start_ms": (start_f / fps) * 1000.0,
                "timeline_length_ms": (dur_f / fps) * 1000.0,
                "source_in_ms": (left_offset / fps) * 1000.0,
            })

        tracks.append({
            "name": timeline.GetTrackName("audio", t_idx) or f"Audio {t_idx}",
            "index": t_idx - 1,
            "is_video": False,
            "is_audio": True,
            "clips": clips,
        })

    data = {
        "project_name": tl_name,
        "frame_rate": fps,
        "source": "DaVinci Resolve",
        "tracks": tracks,
    }

    if not output_json_path:
        bridge_dir = Path.home() / ".timeline_bridge"
        bridge_dir.mkdir(parents=True, exist_ok=True)
        output_json_path = str(bridge_dir / "resolve_timeline.json")

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    log_fn(f"[OK] Exported Resolve timeline to: {output_json_path}")
    return output_json_path

