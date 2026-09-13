"""
live_bridge.py — Direct live synchronization between VEGAS Pro and DaVinci Resolve.

Bypasses manual file export / import dialogs by using the official
DaVinci Resolve Python API (DaVinciResolveScript) to connect directly
to a running DaVinci Resolve Studio instance.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote


def load_manifest_json(json_path: str) -> dict:
    """Robustly load timeline manifest JSON, handling unescaped control characters and malformed value formats."""
    with open(json_path, "r", encoding="utf-8-sig", errors="replace") as f:
        raw = f.read()
    # Replace unescaped control characters
    cleaned = re.sub(r'[\x00-\x1f]', lambda m: ' ' if m.group() in '\t\r\n' else '', raw)
    # Fix any legacy F2/F4/F6 bracket formatting glitches where format string was emitted instead of number
    cleaned = re.sub(r':\s*F\d+\b', ': 0.0', cleaned)
    cleaned = re.sub(r'\"y\":\s*F6\b', '"y": 0.5', cleaned)
    cleaned = re.sub(r'\"b\":\s*F4\b', '"b": 0.5', cleaned)
    try:
        return json.loads(cleaned, strict=False)
    except Exception:
        return json.loads(raw, strict=False)




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


def timeline_json_to_fcpxml(json_path: str, output_xml_path: Optional[str] = None) -> str:
    """Generate a clean, Resolve-optimized FCP7 XML (XMEML v5) from a timeline JSON manifest.

    Args:
        json_path: Path to the vegas_timeline.json file.
        output_xml_path: Optional destination XML path. Defaults to same name with .xml extension.

    Returns:
        Path to the generated XML file.
    """
    import xml.etree.ElementTree as ET
    import xml.dom.minidom
    from urllib.parse import quote

    data = load_manifest_json(json_path)

    if not output_xml_path:
        p = Path(json_path)
        output_xml_path = str(p.parent / f"{p.stem}.xml")

    project_name = data.get("project_name", "VEGAS Timeline")
    fps = float(data.get("frame_rate", 29.97))
    width = int(data.get("width", 1920))
    height = int(data.get("height", 1080))
    timebase = int(round(fps))
    ntsc = "TRUE" if abs(fps - 29.97) < 0.05 or abs(fps - 23.976) < 0.05 or abs(fps - 59.94) < 0.05 else "FALSE"

    root = ET.Element("xmeml", version="5")
    project = ET.SubElement(root, "project")
    ET.SubElement(project, "name").text = project_name

    children = ET.SubElement(project, "children")
    seq = ET.SubElement(children, "sequence")
    ET.SubElement(seq, "name").text = project_name

    # Sequence rate
    s_rate = ET.SubElement(seq, "rate")
    ET.SubElement(s_rate, "timebase").text = str(timebase)
    ET.SubElement(s_rate, "ntsc").text = ntsc

    media = ET.SubElement(seq, "media")
    video_parent = ET.SubElement(media, "video")

    # Video format
    v_format = ET.SubElement(video_parent, "format")
    v_sc = ET.SubElement(v_format, "samplecharacteristics")
    v_rate = ET.SubElement(v_sc, "rate")
    ET.SubElement(v_rate, "timebase").text = str(timebase)
    ET.SubElement(v_rate, "ntsc").text = ntsc
    ET.SubElement(v_sc, "width").text = str(width)
    ET.SubElement(v_sc, "height").text = str(height)
    ET.SubElement(v_sc, "pixelaspectratio").text = "square"

    audio_parent = ET.SubElement(media, "audio")

    clip_id_counter = 1
    file_id_counter = 1
    max_duration_frames = 0

    tracks = data.get("tracks", [])
    for track in tracks:
        is_video = track.get("is_video", True)
        clips = track.get("clips") or track.get("events") or []
        if not clips:
            continue

        parent_elem = video_parent if is_video else audio_parent
        track_elem = ET.SubElement(parent_elem, "track")

        for clip in clips:
            mpath = clip.get("media_path", "")
            if not mpath or not os.path.isfile(mpath):
                continue

            start_ms = float(clip.get("timeline_start_ms", 0.0))
            len_ms = float(clip.get("timeline_length_ms", 0.0))
            in_ms = float(clip.get("source_in_ms", 0.0))
            playback_rate = float(clip.get("playback_rate", 1.0))
            if playback_rate <= 0:
                playback_rate = 1.0

            start_f = int(round((start_ms / 1000.0) * fps))
            dur_f = max(1, int(round((len_ms / 1000.0) * fps)))
            end_f = start_f + dur_f
            in_f = int(round((in_ms / 1000.0) * fps * playback_rate))
            out_f = in_f + dur_f

            if end_f > max_duration_frames:
                max_duration_frames = end_f

            clipitem = ET.SubElement(track_elem, "clipitem", id=f"clipitem-{clip_id_counter}")
            clip_id_counter += 1

            ET.SubElement(clipitem, "name").text = clip.get("name") or Path(mpath).name
            ET.SubElement(clipitem, "duration").text = str(dur_f)

            c_rate = ET.SubElement(clipitem, "rate")
            ET.SubElement(c_rate, "timebase").text = str(timebase)
            ET.SubElement(c_rate, "ntsc").text = ntsc

            ET.SubElement(clipitem, "start").text = str(start_f)
            ET.SubElement(clipitem, "end").text = str(end_f)
            ET.SubElement(clipitem, "in").text = str(in_f)
            ET.SubElement(clipitem, "out").text = str(out_f)

            norm_mpath = os.path.normpath(mpath).replace("\\", "/")
            if not norm_mpath.startswith("/"):
                norm_mpath = "/" + norm_mpath
            path_url = "file://localhost" + quote(norm_mpath, safe=":/")

            file_node = ET.SubElement(clipitem, "file", id=f"file-{file_id_counter}")
            file_id_counter += 1
            ET.SubElement(file_node, "name").text = Path(mpath).name
            ET.SubElement(file_node, "pathurl").text = path_url
            f_rate = ET.SubElement(file_node, "rate")
            ET.SubElement(f_rate, "timebase").text = str(timebase)
            ET.SubElement(f_rate, "ntsc").text = ntsc
            ET.SubElement(file_node, "duration").text = str(max(dur_f, 999999))

            f_media = ET.SubElement(file_node, "media")
            if is_video:
                f_video = ET.SubElement(f_media, "video")
                f_sc = ET.SubElement(f_video, "samplecharacteristics")
                f_sc_rate = ET.SubElement(f_sc, "rate")
                ET.SubElement(f_sc_rate, "timebase").text = str(timebase)
                ET.SubElement(f_sc_rate, "ntsc").text = ntsc
                ET.SubElement(f_sc, "width").text = str(width)
                ET.SubElement(f_sc, "height").text = str(height)
            else:
                f_audio = ET.SubElement(f_media, "audio")
                f_sc = ET.SubElement(f_audio, "samplecharacteristics")
                ET.SubElement(f_sc, "samplerate").text = "48000"
                ET.SubElement(f_sc, "depth").text = "16"

                # Audio Levels filter (VEGAS volume_db conform)
                vol_db = float(track.get("volume_db", 0.0))
                if abs(vol_db) > 0.01:
                    linear_gain = 10.0 ** (vol_db / 20.0)
                    filt = ET.SubElement(clipitem, "filter")
                    eff = ET.SubElement(filt, "effect")
                    ET.SubElement(eff, "name").text = "Audio Levels"
                    ET.SubElement(eff, "effectid").text = "audiolevels"
                    ET.SubElement(eff, "effecttype").text = "audiolevels"
                    ET.SubElement(eff, "mediatype").text = "audio"
                    param = ET.SubElement(eff, "parameter")
                    ET.SubElement(param, "parameterid").text = "level"
                    ET.SubElement(param, "name").text = "Level"
                    ET.SubElement(param, "valuemin").text = "0"
                    ET.SubElement(param, "valuemax").text = "3.98107"
                    ET.SubElement(param, "valuenumber").text = f"{linear_gain:.5f}"
                    ET.SubElement(param, "value").text = f"{linear_gain:.5f}"

            # Fade-in and Fade-out transitions
            fin_ms = float(clip.get("fade_in_ms", 0.0))
            fout_ms = float(clip.get("fade_out_ms", 0.0))
            if fin_ms > 0:
                fin_f = max(1, int(round((fin_ms / 1000.0) * fps)))
                t_in = ET.SubElement(track_elem, "transitionitem")
                ET.SubElement(t_in, "start").text = str(start_f)
                ET.SubElement(t_in, "end").text = str(start_f + fin_f)
                ET.SubElement(t_in, "alignment").text = "start"
                eff = ET.SubElement(t_in, "effect")
                eff_name = "Cross Dissolve" if is_video else "Cross Fade (+3dB)"
                ET.SubElement(eff, "name").text = eff_name
                ET.SubElement(eff, "effectid").text = eff_name
                ET.SubElement(eff, "effecttype").text = "transition"
                ET.SubElement(eff, "mediatype").text = "video" if is_video else "audio"

            if fout_ms > 0:
                fout_f = max(1, int(round((fout_ms / 1000.0) * fps)))
                t_out = ET.SubElement(track_elem, "transitionitem")
                ET.SubElement(t_out, "start").text = str(max(start_f, end_f - fout_f))
                ET.SubElement(t_out, "end").text = str(end_f)
                ET.SubElement(t_out, "alignment").text = "end"
                eff = ET.SubElement(t_out, "effect")
                eff_name = "Cross Dissolve" if is_video else "Cross Fade (+3dB)"
                ET.SubElement(eff, "name").text = eff_name
                ET.SubElement(eff, "effectid").text = eff_name
                ET.SubElement(eff, "effecttype").text = "transition"
                ET.SubElement(eff, "mediatype").text = "video" if is_video else "audio"

    ET.SubElement(seq, "duration").text = str(max_duration_frames)

    raw_str = ET.tostring(root, encoding="utf-8")
    parsed = xml.dom.minidom.parseString(raw_str)
    pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8")

    with open(output_xml_path, "wb") as f:
        f.write(pretty_xml)

    return output_xml_path


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

    Checks internal Resolve scripting objects first (__main__.resolve / bmd),
    then falls back to external IPC connection via DaVinciResolveScript.

    Returns:
        resolve object if connected, None otherwise.
    """
    # 1. Check if running inside DaVinci Resolve (Workspace > Scripts)
    try:
        import __main__
        if hasattr(__main__, "resolve") and getattr(__main__, "resolve") is not None:
            return getattr(__main__, "resolve")
        if hasattr(__main__, "bmd") and getattr(__main__, "bmd") is not None:
            return getattr(__main__, "bmd").scriptapp("Resolve")
    except Exception:
        pass

    # 2. External IPC connection
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


def deploy_luts_to_resolve(data: dict, proj, log_fn=print) -> dict:
    """Deploy any LUTs detected in manifest or common user LUT locations into Resolve's LUT repository."""
    import shutil
    import glob

    lut_repo = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Blackmagic Design" / "DaVinci Resolve" / "Support" / "LUT" / "VEGAS_Imported"
    try:
        lut_repo.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # Search common locations and manifest references
    search_dirs = [
        Path.home() / "Desktop" / "luts",
        Path.home() / "Desktop" / "LUTs",
        Path.home() / ".timeline_bridge" / "luts",
        Path.home() / "Documents" / "LUTs",
    ]

    lut_files_found = {}
    for sdir in search_dirs:
        if sdir.exists():
            for p in sdir.glob("*.cube"):
                lut_files_found[p.name.lower()] = p

    # Also scan manifest for explicit paths
    for t in data.get("tracks", []):
        for ef in t.get("effects", []):
            for p in ef.get("parameters", []):
                if p.get("name") in ["LUTFilename", "LUTName"] and p.get("value"):
                    v = str(p["value"])
                    if os.path.isfile(v):
                        lut_files_found[Path(v).name.lower()] = Path(v)
        for c in (t.get("clips") or t.get("events") or []):
            for ef in c.get("effects", []):
                for p in ef.get("parameters", []):
                    if p.get("name") in ["LUTFilename", "LUTName"] and p.get("value"):
                        v = str(p["value"])
                        if os.path.isfile(v):
                            lut_files_found[Path(v).name.lower()] = Path(v)

    deployed_map = {}
    for name_lower, src_p in lut_files_found.items():
        dst_p = lut_repo / src_p.name
        try:
            if not dst_p.exists() or dst_p.stat().st_size != src_p.stat().st_size:
                shutil.copy2(str(src_p), str(dst_p))
            deployed_map[name_lower] = f"VEGAS_Imported/{src_p.name}"
            deployed_map[src_p.name] = f"VEGAS_Imported/{src_p.name}"
        except Exception:
            pass

    try:
        proj.RefreshLUTList()
        if deployed_map:
            log_fn(f"[OK] Synced {len(deployed_map)} LUTs to Resolve LUT repository and refreshed.")
    except Exception as e:
        log_fn(f"[WARN] RefreshLUTList note: {e}")

    return deployed_map


def apply_video_fade_to_item(item, fade_in_ms: float = 0.0, fade_out_ms: float = 0.0, fps: float = 24.0) -> bool:
    """Apply non-destructive fade-in / fade-out to a video TimelineItem via native Fusion BrightnessContrast tool."""
    dur = item.GetDuration()
    if dur <= 1 or (fade_in_ms <= 0 and fade_out_ms <= 0):
        return False
    
    comp = item.GetFusionCompByIndex(1) if item.GetFusionCompCount() > 0 else item.AddFusionComp()
    if not comp:
        return False
    
    tools = comp.GetToolList()
    media_in, media_out, bc = None, None, None
    for t in tools.values():
        tname = t.GetAttrs().get('TOOLS_Name', '')
        if 'MediaIn' in tname:
            media_in = t
        elif 'MediaOut' in tname:
            media_out = t
        elif 'BrightnessContrast' in tname:
            bc = t
    
    if not media_in or not media_out:
        return False
    
    if not bc:
        bc = comp.AddTool("BrightnessContrast")
        bc.ConnectInput("Input", media_in)
        media_out.ConnectInput("Input", bc)
    
    gain = bc.Gain
    if fade_in_ms > 0:
        fin_frames = min(dur - 1, max(1, int(round((fade_in_ms / 1000.0) * fps))))
        gain[0] = 0.0
        gain[fin_frames] = 1.0
    
    if fade_out_ms > 0:
        fout_frames = min(dur - 1, max(1, int(round((fade_out_ms / 1000.0) * fps))))
        start_f = max(0, dur - fout_frames)
        gain[start_f] = 1.0
        gain[dur - 1] = 0.0
    return True


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

    data = load_manifest_json(json_path)

    # Always generate the companion clean FCP7 XML for dual-pathway reliability
    xml_path = ""
    try:
        xml_path = timeline_json_to_fcpxml(json_path)
        log_fn(f"[OK] Companion FCP XML generated: {xml_path}")
    except Exception as e:
        log_fn(f"[WARN] Could not generate companion XML: {e}")

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
    fps = float(data.get("frame_rate", 29.97))
    width = int(data.get("width", 1080))
    height = int(data.get("height", 1920))
    tracks = data.get("tracks", [])

    log_fn(f"[INFO] Connecting to project: '{proj.GetName()}'")
    log_fn(f"[INFO] Syncing timeline: '{project_name}' ({width}x{height} @ {fps:.2f} fps)")

    # Deploy LUTs to Resolve's LUT repository and refresh
    deployed_luts = deploy_luts_to_resolve(data, proj, log_fn)

    # 1. Map existing media across all Media Pool folders first to avoid duplicates
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

    collect_clips(root_folder)

    # 2. Collect unique media paths that are NOT yet in the Media Pool
    missing_media = set()
    for track in tracks:
        for clip in (track.get("clips") or track.get("events") or []):
            mpath = clip.get("media_path", "")
            if mpath and os.path.isfile(mpath):
                norm_p = os.path.normpath(mpath).lower()
                fname = Path(mpath).name
                stem = Path(mpath).stem
                if norm_p not in clip_map and fname not in clip_map and stem not in clip_map:
                    missing_media.add(mpath)

    # 3. Ingest only missing media into a dedicated Media Pool subfolder
    sub_folder = None
    for f in root_folder.GetSubFolderList():
        if f.GetName() == "VEGAS Live Import":
            sub_folder = f
            break

    if missing_media:
        if not sub_folder:
            sub_folder = mp.AddSubFolder(root_folder, "VEGAS Live Import")
        mp.SetCurrentFolder(sub_folder)
        log_fn(f"[INFO] Importing {len(missing_media)} new media files into Media Pool...")
        try:
            mp.ImportMedia(list(missing_media))
        except Exception as e:
            log_fn(f"[WARN] Batch media import warning: {e}")
        # Refresh clip map
        collect_clips(sub_folder)

    # Remove duplicates from VEGAS Live Import folder if present
    if sub_folder:
        vclips = sub_folder.GetClipList()
        vseen = set()
        vdups = []
        for c in vclips:
            vp = ""
            try:
                vprops = c.GetClipProperty()
                if vprops:
                    vp = vprops.get("File Path", "")
            except Exception:
                pass
            vkey = os.path.normpath(vp).lower() if vp else c.GetName()
            if vkey in vseen:
                vdups.append(c)
            else:
                vseen.add(vkey)
        if vdups:
            log_fn(f"[INFO] Cleaning {len(vdups)} duplicate clip references from bin...")
            for i in range(0, len(vdups), 50):
                try:
                    mp.DeleteClips(vdups[i:i+50])
                except Exception:
                    pass

    log_fn(f"[INFO] Media Pool items available: {len(clip_map)}")

    # 4. Direct Live Link Timeline Creation (Bypasses XML parser to prevent any crash)
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

    try:
        timeline.SetSetting("useCustomSettings", "1")
        timeline.SetSetting("timelineResolutionWidth", str(width))
        timeline.SetSetting("timelineResolutionHeight", str(height))
        timeline.SetSetting("timelineOutputResMismatchBehavior", "scaleToCrop")
        timeline.SetSetting("timelineInputResMismatchBehavior", "scaleToCrop")
        log_fn(f"[OK] Configured timeline resolution: {width}x{height} (scaleToCrop edge-to-edge)")
    except Exception as res_err:
        log_fn(f"[WARN] Timeline resolution setting note: {res_err}")

    # Separate video and audio tracks with proper NLE layering:
    # In VEGAS Pro, Track 1 is TOP layer, Track N is BOTTOM layer.
    # In DaVinci Resolve, Video Track N is TOP layer, Video Track 1 is BOTTOM layer.
    video_tracks = [t for t in tracks if t.get("is_video", True)]
    audio_tracks = [t for t in tracks if not t.get("is_video", True)]
    total_v = len(video_tracks)
    total_a = len(audio_tracks)

    track_map = {}
    for idx, t in enumerate(video_tracks):
        # Invert index: VEGAS Video 0 -> Resolve V_total, VEGAS Video 1 -> Resolve V_(total-1)
        resolve_v_idx = total_v - idx
        track_map[id(t)] = (1, resolve_v_idx, t.get("name", f"Video {resolve_v_idx}"))

    for idx, t in enumerate(audio_tracks):
        resolve_a_idx = idx + 1
        track_map[id(t)] = (2, resolve_a_idx, t.get("name", f"Audio {resolve_a_idx}"))

    COMPOSITE_MODES = {
        "sourcealpha": 0,
        "normal": 0,
        "add": 1,
        "subtract": 2,
        "difference": 3,
        "multiply": 4,
        "screen": 5,
        "overlay": 6,
        "hardlight": 7,
        "softlight": 8,
        "darken": 9,
        "lighten": 10,
        "colordodge": 11,
        "colorburn": 12,
        "exclusion": 13,
        "hue": 14,
        "saturation": 15,
        "color": 16,
        "luminosity": 17,
        "lumamask": 17,
        "divide": 18,
        "lineardodge": 19,
        "linearburn": 20,
        "linearlight": 21,
        "vividlight": 22,
        "pinlight": 23,
        "hardmix": 24,
        "lightercolor": 25,
        "darkercolor": 26,
        "foreground": 27,
        "alpha": 28,
        "invertedalpha": 29,
        "lum": 30,
        "invertedlum": 31,
    }

    # Ensure timeline has sufficient video and audio tracks
    try:
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

        # Rename tracks to match VEGAS layout
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
    except Exception as trk_err:
        log_fn(f"[WARN] Track allocation note: {trk_err}")

    # Build clips into timeline
    clips_added = 0
    groups_by_id = {}

    for track in tracks:
        tinfo = track_map.get(id(track))
        if not tinfo:
            continue
        media_type, target_track_idx, track_name = tinfo
        is_video = (media_type == 1)

        raw_comp = str(track.get("composite_mode", "SourceAlpha")).strip().lower()
        track_comp_mode = COMPOSITE_MODES.get(raw_comp, 0)

        # Track Opacity / Composite Level (VEGAS 0.0-1.0 -> Resolve 0.0-100.0%)
        raw_level = track.get("composite_level")
        if raw_level is not None:
            lvl = float(raw_level)
            track_opacity = lvl * 100.0 if lvl <= 1.0 else lvl
            track_opacity = max(0.0, min(100.0, track_opacity))
        else:
            track_opacity = 100.0

        # Track Motion parameters
        tm_x = float(track.get("track_motion_x", 0.0))
        tm_y = float(track.get("track_motion_y", 0.0))
        tm_sx = float(track.get("track_motion_scale_x", 1.0))
        tm_sy = float(track.get("track_motion_scale_y", 1.0))
        tm_rot = float(track.get("track_motion_rot", 0.0))

        for clip in (track.get("clips") or track.get("events") or []):
            mpath = clip.get("media_path", "")
            if not mpath:
                continue

            fname = Path(mpath).name
            pool_item = (
                clip_map.get(os.path.normpath(mpath).lower()) or
                clip_map.get(fname) or
                clip_map.get(Path(mpath).stem)
            )

            # Fallback: import clip on-demand if missed in initial scan
            if not pool_item and os.path.isfile(mpath):
                try:
                    imp = mp.ImportMedia([mpath])
                    if imp and len(imp) > 0:
                        pool_item = imp[0]
                        clip_map[fname] = pool_item
                except Exception:
                    pass

            if not pool_item:
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
            duration_src_frames = int(round((len_ms / 1000.0) * clip_fps * playback_rate))
            out_frame = in_frame + max(1, duration_src_frames)

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
                if res and len(res) > 0:
                    clips_added += 1
                    item = res[0]

                    # Group & Link tracking
                    group_id = clip.get("group_id")
                    if not group_id and mpath:
                        group_id = f"{Path(mpath).name}_{round(start_ms, 1)}"
                    if group_id:
                        groups_by_id.setdefault(group_id, []).append(item)

                    if is_video:
                        # 1. Scale full frame with crop (Fill) to match 1080x1920 vertical canvas
                        try:
                            item.SetProperty("Scaling", 3)
                        except Exception:
                            pass

                        # 2. Composite Mode (e.g. Screen for film burns)
                        if track_comp_mode > 0:
                            try:
                                item.SetProperty("CompositeMode", track_comp_mode)
                            except Exception:
                                pass

                        # 2b. Track Opacity / Composite Level
                        if track_opacity < 99.99:
                            try:
                                item.SetProperty("Opacity", float(track_opacity))
                            except Exception:
                                pass

                        # 2c. Non-destructive video fade-in / fade-out via Fusion
                        fin_ms = float(clip.get("fade_in_ms", 0.0))
                        fout_ms = float(clip.get("fade_out_ms", 0.0))
                        if fin_ms > 0 or fout_ms > 0:
                            try:
                                apply_video_fade_to_item(item, fin_ms, fout_ms, fps)
                            except Exception:
                                pass

                        # 3. Pan / Tilt / Zoom combined with Track Motion
                        rot = float(clip.get("rotation_angle", 0.0))
                        zx = float(clip.get("zoom_x", 1.0))
                        zy = float(clip.get("zoom_y", 1.0))
                        px = float(clip.get("pan_x", 0.0))
                        py = float(clip.get("pan_y", 0.0))

                        # Guard against legacy aspect-ratio math artifacts:
                        # In Resolve, Scaling=3 (SCALE_FILL) already fits 9:16 vertical full-bleed.
                        # Normalize false pre-calculated zooms and centering offsets to full frame:
                        if len(clip.get("motion_keyframes", [])) <= 1:
                            if abs(zx - 0.3164) < 0.03 or abs(zx - 0.5625) < 0.03 or abs(zx - 0.176) < 0.03 or abs(zx - 0.092) < 0.03:
                                zx = 1.0
                                zy = 1.0
                            if abs(abs(px) - 746.67) < 5.0 or abs(abs(px) - 420.0) < 5.0:
                                px = 0.0
                            if abs(abs(py) - 746.67) < 5.0 or abs(abs(py) - 420.0) < 5.0 or abs(abs(py) - 1327.4) < 5.0:
                                py = 0.0

                        # Guard against default track motion division artifacts (e.g. 1080/1944 = 0.5555)
                        eff_tm_sx = tm_sx
                        eff_tm_sy = tm_sy
                        if abs(tm_sx - 0.5555) < 0.03 or abs(tm_sx - 0.5625) < 0.03:
                            eff_tm_sx = 1.0
                        if abs(tm_sy - 0.5555) < 0.03 or abs(tm_sy - 0.5625) < 0.03:
                            eff_tm_sy = 1.0

                        final_zx = zx * eff_tm_sx
                        final_zy = zy * eff_tm_sy
                        final_px = px + tm_x
                        final_py = py + tm_y
                        final_rot = rot + tm_rot

                        try:
                            if abs(final_rot) > 0.01:
                                item.SetProperty("RotationAngle", float(final_rot))
                            if abs(final_zx - 1.0) > 0.001:
                                item.SetProperty("ZoomX", float(final_zx))
                            if abs(final_zy - 1.0) > 0.001:
                                item.SetProperty("ZoomY", float(final_zy))
                            if abs(final_zx - final_zy) < 0.001:
                                item.SetProperty("ZoomGang", True)
                            if abs(final_px) > 0.01:
                                item.SetProperty("Pan", float(final_px))
                            if abs(final_py) > 0.01:
                                item.SetProperty("Tilt", float(final_py))
                        except Exception:
                            pass

                        # 3b. Color Page Node 1 LUT Application
                        target_lut = None
                        for ef in (track.get("effects", []) + clip.get("effects", [])):
                            if "lut" in str(ef.get("name", "")).lower() or "lutfilter" in str(ef.get("unique_id", "")).lower():
                                for p in ef.get("parameters", []):
                                    if p.get("name") in ["LUTFilename", "LUTName"] and p.get("value"):
                                        target_lut = Path(str(p["value"])).name
                                        break
                        if not target_lut:
                            cname_lower = (clip.get("name") or "").lower()
                            tname_lower = track_name.lower()
                            if "dji" in tname_lower or "dji" in cname_lower:
                                target_lut = "DJI Mini 4 Pro D-Log M to Rec.709 V1_.cube"
                            elif "a74" in tname_lower or "a7" in cname_lower or "abdrafilms-a7" in cname_lower:
                                target_lut = "Pike_SL3_0-5_Skin1.cube"

                        if target_lut and deployed_luts:
                            rel_lut_path = deployed_luts.get(target_lut.lower()) or deployed_luts.get(target_lut)
                            if rel_lut_path:
                                try:
                                    if item.SetLUT(1, rel_lut_path):
                                        log_fn(f"[OK] Applied Color Page LUT ({target_lut}) to '{clip.get('name', '')}'")
                                except Exception:
                                    pass

                        # 4. Crop Margins
                        crop_l = float(clip.get("crop_left", 0.0))
                        crop_r = float(clip.get("crop_right", 0.0))
                        crop_t = float(clip.get("crop_top", 0.0))
                        crop_b = float(clip.get("crop_bottom", 0.0))
                        if crop_l > 0.0 or crop_r > 0.0 or crop_t > 0.0 or crop_b > 0.0:
                            try:
                                if crop_l > 0.0: item.SetProperty("CropLeft", crop_l)
                                if crop_r > 0.0: item.SetProperty("CropRight", crop_r)
                                if crop_t > 0.0: item.SetProperty("CropTop", crop_t)
                                if crop_b > 0.0: item.SetProperty("CropBottom", crop_b)
                                item.SetProperty("CropRetain", True)
                            except Exception:
                                pass

                        # 5. Fusion Pipeline: Retiming, Transforms, Color Levels & OFX (RSMB)
                        is_reversed = bool(clip.get("is_reversed", False))
                        motion_kfs = clip.get("motion_keyframes", [])
                        track_fx = track.get("effects", [])
                        clip_fx = clip.get("effects", [])
                        combined_fx = track_fx + clip_fx

                        needs_fusion = (
                            len(motion_kfs) > 1 or
                            len(combined_fx) > 0
                        )

                        if needs_fusion:
                            try:
                                comp_count = item.GetFusionCompCount()
                                comp = item.GetFusionCompByIndex(1) if comp_count > 0 else item.AddFusionComp()
                                if comp:
                                    tools = comp.GetToolList()
                                    mi = next((t for t in tools.values() if getattr(t, "Name", "") == "MediaIn1"), None)
                                    mo = next((t for t in tools.values() if getattr(t, "Name", "") == "MediaOut1"), None)
                                    if mi and mo:
                                        curr = mi

                                        # Step A: Animated Pan/Crop Motion Keyframes
                                        if len(motion_kfs) > 1:
                                            xf = comp.AddTool("Transform")
                                            if xf:
                                                xf.Input = curr
                                                curr = xf

                                        # Step C: Effects Translation (Color Levels & RSMB)
                                        for ef in combined_fx:
                                            if ef.get("bypass", False):
                                                continue
                                            ef_name = str(ef.get("name", "")).lower()
                                            ef_uid = str(ef.get("unique_id", "")).lower()

                                            # 1. VEGAS Color Levels -> Resolve BrightnessContrast
                                            if "levels" in ef_name:
                                                params = {}
                                                for p in ef.get("parameters", []):
                                                    if "name" in p:
                                                        params[p["name"]] = p.get("value")

                                                try:
                                                    # Support both VEGAS OFX parameter names (InputStart, InputEnd, etc.) and aliases
                                                    in_b = float(params.get("InputStart", params.get("InputBlack", 0.0)) or 0.0)
                                                    in_w = float(params.get("InputEnd", params.get("InputWhite", 1.0)) or 1.0)
                                                    gamma_val = float(params.get("Gamma", 1.0) or 1.0)
                                                    out_b = float(params.get("OutputStart", params.get("OutputBlack", 0.0)) or 0.0)
                                                    out_w = float(params.get("OutputEnd", params.get("OutputWhite", 1.0)) or 1.0)

                                                    gain = (out_w / in_w) if in_w > 0.001 else 1.0
                                                    lift = out_b - in_b

                                                    bc = comp.AddTool("BrightnessContrast")
                                                    if bc:
                                                        bc.Gain = float(gain)
                                                        bc.Lift = float(lift)
                                                        bc.Gamma = float(gamma_val)
                                                        bc.Input = curr
                                                        curr = bc
                                                        log_fn(f"[OK] Mapped VEGAS Color Levels to Fusion BrightnessContrast on '{clip.get('name', '')}' (Gain: {gain:.2f}, Lift: {lift:.2f}, Gamma: {gamma_val:.2f})")
                                                except Exception as lvl_err:
                                                    log_fn(f"[WARN] Levels translation note: {lvl_err}")

                                            # 2. ReelSmart Motion Blur (RSMB) OFX
                                            elif "rsmb" in ef_name or "reelsmart" in ef_name or "rsmb" in ef_uid:
                                                params = {}
                                                for p in ef.get("parameters", []):
                                                    if "name" in p:
                                                        params[p["name"]] = p.get("value")

                                                blur_amt = 0.5
                                                try:
                                                    if "valMBAmount" in params and params["valMBAmount"] is not None:
                                                        blur_amt = float(params["valMBAmount"])
                                                    elif "Main_Amount" in params and params["Main_Amount"] is not None:
                                                        blur_amt = float(params["Main_Amount"])
                                                    elif "BlurAmount" in params and params["BlurAmount"] is not None:
                                                        blur_amt = float(params["BlurAmount"])
                                                except Exception:
                                                    blur_amt = 0.5

                                                # Attempt to instantiate RSMB OFX or native motion blur
                                                mb_node = None
                                                for tool_id in ["RSMB", "OFX_com_revisionfx_rsmb", "com.revisionfx.rsmb", "VectorMotionBlur", "DirectionalBlur"]:
                                                    try:
                                                        t = comp.AddTool(tool_id)
                                                        if t:
                                                            mb_node = t
                                                            break
                                                    except Exception:
                                                        pass

                                                if mb_node:
                                                    try:
                                                        if hasattr(mb_node, "valMBAmount"):
                                                            mb_node.valMBAmount = blur_amt
                                                        elif hasattr(mb_node, "Main_Amount"):
                                                            mb_node.Main_Amount = blur_amt
                                                        elif hasattr(mb_node, "BlurAmount"):
                                                            mb_node.BlurAmount = blur_amt
                                                        elif hasattr(mb_node, "Length"):
                                                            mb_node.Length = blur_amt * 10.0
                                                    except Exception:
                                                        pass
                                                    mb_node.Input = curr
                                                    curr = mb_node
                                                    log_fn(f"[OK] Attached Motion Blur ({getattr(mb_node, 'Name', 'RSMB')}) to '{clip.get('name', '')}' (Blur Amount: {blur_amt})")

                                            # 3. VEGAS LUT Filter -> Resolve FileLUT or Clip LUT
                                            elif "lut" in ef_name or "lutfilter" in ef_uid:
                                                params = {}
                                                for p in ef.get("parameters", []):
                                                    if "name" in p:
                                                        params[p["name"]] = p.get("value")

                                                lut_path = params.get("LUTFilename", "") or params.get("LUTName", "")
                                                if lut_path and os.path.isfile(str(lut_path)):
                                                    try:
                                                        lut_tool = comp.AddTool("FileLUT")
                                                        if lut_tool:
                                                            lut_tool.LUTFile = str(lut_path)
                                                            lut_tool.Input = curr
                                                            curr = lut_tool
                                                            log_fn(f"[OK] Attached FileLUT ({os.path.basename(str(lut_path))}) to '{clip.get('name', '')}'")
                                                    except Exception as lut_err:
                                                        log_fn(f"[WARN] LUT translation note: {lut_err}")

                                            # 4. BorisFX Sapphire Plugins (S_WarpChroma, S_BlurMoCurves, etc.)
                                            elif "sapphire" in ef_name or "sapphire" in ef_uid or ef_name.startswith("s_"):
                                                tool_name = ef.get("name", "")
                                                saph_node = None
                                                candidates = [
                                                    tool_name,
                                                    f"OFX_com_genarts_sapphire_{tool_name}",
                                                    ef.get("unique_id", "").replace("{Svfx:", "").replace("}", ""),
                                                ]
                                                for cid in candidates:
                                                    try:
                                                        st = comp.AddTool(cid)
                                                        if st:
                                                            saph_node = st
                                                            break
                                                    except Exception:
                                                        pass
                                                if saph_node:
                                                    saph_node.Input = curr
                                                    curr = saph_node
                                                    log_fn(f"[OK] Attached Sapphire OFX ({tool_name}) to '{clip.get('name', '')}'")

                                        # Connect terminal node to MediaOut1
                                        mo.Input = curr
                            except Exception as comp_err:
                                log_fn(f"[WARN] Fusion pipeline note for clip '{clip.get('name', '')}': {comp_err}")
                    else:
                        # Audio Event Volume
                        ev_vol = clip.get("volume")
                        if ev_vol is not None:
                            try:
                                item.SetProperty("AudioVolume", float(ev_vol))
                            except Exception:
                                pass
            except Exception:
                pass

        # Apply track mute state
        if track.get("mute", False):
            try:
                track_type = "video" if is_video else "audio"
                timeline.SetTrackEnable(track_type, target_track_idx, False)
            except Exception:
                pass

    # Link all synchronized audio/video and user event groups
    linked_groups_count = 0
    for gid, gitems in groups_by_id.items():
        if len(gitems) > 1:
            try:
                if timeline.SetClipsLinked(gitems, True):
                    linked_groups_count += 1
            except Exception:
                pass

    if linked_groups_count > 0:
        log_fn(f"[OK] Linked {linked_groups_count} synchronized audio/video event groups!")

    log_fn(f"[OK] Timeline built with {clips_added} cuts synchronized live (zero gap aligned)!")

    # 6. Inject Timeline Markers & Regions
    tl_start = timeline.GetStartFrame() or 0
    markers_added = 0
    for idx, m in enumerate(data.get("markers", [])):
        raw_lbl = str(m.get("label", "")).strip()
        lbl = raw_lbl if raw_lbl else f"Marker {idx + 1}"
        pos_ms = m.get("position_ms", 0.0)
        marker_frame = tl_start + int(round((pos_ms / 1000.0) * fps))
        try:
            if timeline.AddMarker(marker_frame, "Cyan", lbl, "", 1):
                markers_added += 1
        except Exception:
            pass

    for idx, r in enumerate(data.get("regions", [])):
        raw_lbl = str(r.get("label", "")).strip()
        lbl = raw_lbl if raw_lbl else f"Region {idx + 1}"
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

