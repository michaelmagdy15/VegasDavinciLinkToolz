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

    with open(json_path, "r", encoding="utf-8") as f:
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

    # Map filename to MediaPoolItem
    clip_map = {}
    for c in sub_folder.GetClipList():
        clip_map[c.GetName()] = c

    log_fn(f"[INFO] Media Pool items ready: {len(clip_map)}")

    # 4. Create timeline
    timeline_name = f"{project_name} (VEGAS Sync)"
    timeline = mp.CreateEmptyTimeline(timeline_name)
    if not timeline:
        log_fn(f"[ERROR] Failed to create timeline '{timeline_name}' in Resolve.")
        return False

    proj.SetCurrentTimeline(timeline)
    log_fn(f"[OK] Created timeline: '{timeline_name}'")

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
            in_ms = clip.get("source_in_ms", 0.0)

            # Convert ms to frames
            start_frame = int(round((start_ms / 1000.0) * fps))
            duration_frames = int(round((len_ms / 1000.0) * fps))
            in_frame = int(round((in_ms / 1000.0) * fps))
            out_frame = in_frame + duration_frames

            clip_info = {
                "mediaPoolItem": pool_item,
                "startFrame": in_frame,
                "endFrame": out_frame,
                "recordFrame": start_frame,
                "trackIndex": track_idx,
                "mediaType": 1 if is_video else 2,
            }

            try:
                if mp.AppendToTimeline([clip_info]):
                    clips_added += 1
            except Exception:
                pass

    log_fn(f"[OK] Timeline built with {clips_added} cuts synchronized live!")
    return True
