"""
ai_scout.py — Automated Motion & Visual Action Scout for Video Footage.

Analyzes video clips using hardware-accelerated FFmpeg frame sampling (NVIDIA CUDA + RTX NVDEC with CPU fallback),
detects peak action moments (jumps, carves, kiteloops, water spray, cinematic flyovers),
and generates pre-trimmed selects manifests for VEGAS Pro and DaVinci Resolve.
"""

import os
import sys
import glob
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np


def get_clip_info(file_path: str) -> Dict[str, Any]:
    """Return video duration in seconds, pix_fmt, and dimensions via ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,pix_fmt,codec_name:format=duration",
        "-of", "json",
        file_path,
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
        data = json.loads(res.stdout)
        st = data.get("streams", [{}])[0]
        fmt = data.get("format", {})
        dur = float(fmt.get("duration", 0.0))
        return {
            "duration": dur,
            "pix_fmt": st.get("pix_fmt", "yuv420p"),
            "codec_name": st.get("codec_name", "hevc"),
            "width": int(st.get("width", 1920)),
            "height": int(st.get("height", 1080)),
        }
    except Exception:
        return {"duration": 0.0, "pix_fmt": "yuv420p", "codec_name": "unknown", "width": 1920, "height": 1080}


def get_clip_duration_seconds(file_path: str) -> float:
    """Return video duration in seconds via ffprobe."""
    info = get_clip_info(file_path)
    return info.get("duration", 0.0)


def sample_video_frames(
    file_path: str,
    fps_sample: float = 1.0,
    w: int = 160,
    h: int = 90,
) -> Tuple[Optional[np.ndarray], float, float]:
    """Sample video frames downscaled to w x h grayscale using CUDA GPU acceleration or CPU fallback.

    Returns:
        (frames_array [N, h, w], effective_fps, duration_seconds)
    """
    info = get_clip_info(file_path)
    duration = info.get("duration", 0.0)
    if duration < 0.5:
        return None, fps_sample, 0.0

    pix_fmt = info.get("pix_fmt", "")
    is_10bit = "10" in pix_fmt

    # 1. Attempt hardware-accelerated CUDA decode with on-GPU scale
    try:
        hw_fmt = "p010le" if is_10bit else "nv12"
        cmd = [
            "ffmpeg", "-y",
            "-hwaccel", "cuda",
            "-hwaccel_output_format", "cuda",
            "-i", file_path,
            "-vf", f"fps={fps_sample},scale_cuda={w}:{h},hwdownload,format={hw_fmt}",
            "-f", "rawvideo",
            "-",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        raw_bytes = proc.stdout.read()
        proc.wait()

        if proc.returncode == 0 and len(raw_bytes) > 0:
            if is_10bit:
                frame_bytes = int(w * h * 3)  # p010le: Y (w*h*2) + UV (w*h)
                num_frames = len(raw_bytes) // frame_bytes
                if num_frames >= 2:
                    y_bytes = w * h * 2
                    frames = []
                    for i in range(num_frames):
                        offset = i * frame_bytes
                        y_plane = np.frombuffer(raw_bytes[offset:offset + y_bytes], dtype=np.uint16).reshape((h, w))
                        frames.append((y_plane >> 8).astype(np.uint8))
                    effective_fps = num_frames / duration if duration > 0 else fps_sample
                    return np.array(frames, dtype=np.uint8), effective_fps, duration
            else:
                frame_bytes = int(w * h * 1.5)  # nv12: Y (w*h) + UV (w*h*0.5)
                num_frames = len(raw_bytes) // frame_bytes
                if num_frames >= 2:
                    y_bytes = w * h
                    frames = []
                    for i in range(num_frames):
                        offset = i * frame_bytes
                        y_plane = np.frombuffer(raw_bytes[offset:offset + y_bytes], dtype=np.uint8).reshape((h, w))
                        frames.append(y_plane)
                    effective_fps = num_frames / duration if duration > 0 else fps_sample
                    return np.array(frames, dtype=np.uint8), effective_fps, duration
    except Exception:
        pass

    # 2. Graceful CPU fallback (scale and format=gray)
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", file_path,
            "-vf", f"fps={fps_sample},scale={w}:{h},format=gray",
            "-f", "rawvideo",
            "-",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        raw_bytes = proc.stdout.read()
        proc.wait()

        frame_size = w * h
        num_frames = len(raw_bytes) // frame_size
        if num_frames >= 2:
            frames = np.frombuffer(raw_bytes[: num_frames * frame_size], dtype=np.uint8).reshape((num_frames, h, w))
            effective_fps = num_frames / duration if duration > 0 else fps_sample
            return frames, effective_fps, duration
    except Exception:
        pass

    return None, fps_sample, duration


def analyze_clip_action(
    file_path: str,
    fps_sample: float = 1.0,
    target_duration_s: float = 3.5,
    max_peaks: int = 3,
) -> List[Dict[str, Any]]:
    """Sample video to compute visual motion delta and detect peak action/promo moments.

    Returns a list of peak action segments (1 to 3 depending on clip length).
    Each segment contains:
        source_in_ms: Start time in milliseconds
        length_ms: Duration in milliseconds
        score: Normalized action score (0.0 to 1.0)
    """
    frames, effective_fps, duration = sample_video_frames(file_path, fps_sample=fps_sample)
    if duration < 1.0:
        return []

    # If clip is short (<= target_duration_s + 0.5), return whole clip
    if duration <= target_duration_s + 0.5:
        return [{
            "source_in_ms": 0.0,
            "length_ms": round(duration * 1000.0, 2),
            "score": 0.5,
        }]

    if frames is None or len(frames) < 2:
        return [{
            "source_in_ms": 0.0,
            "length_ms": round(min(duration, target_duration_s) * 1000.0, 2),
            "score": 0.5,
        }]

    num_frames = len(frames)
    diffs = np.zeros(num_frames - 1, dtype=np.float32)
    for i in range(num_frames - 1):
        diffs[i] = np.mean(np.abs(frames[i + 1].astype(np.float32) - frames[i].astype(np.float32)))

    if len(diffs) == 0:
        return []

    window_frames = max(1, int(round(target_duration_s * effective_fps)))
    if len(diffs) <= window_frames:
        return [{
            "source_in_ms": 0.0,
            "length_ms": round(min(duration, target_duration_s) * 1000.0, 2),
            "score": round(float(np.mean(diffs)), 3),
        }]

    kernel = np.ones(window_frames) / window_frames
    smoothed = np.convolve(diffs, kernel, mode="valid")

    segments = []

    # 1. Primary peak (highest motion moment)
    best_idx = int(np.argmax(smoothed))
    peak_score = float(smoothed[best_idx])
    start_sec = max(0.0, best_idx / effective_fps)
    end_sec = min(duration, start_sec + target_duration_s)
    actual_dur = end_sec - start_sec

    segments.append({
        "source_in_ms": round(start_sec * 1000.0, 2),
        "length_ms": round(actual_dur * 1000.0, 2),
        "score": round(min(1.0, peak_score / 25.0), 3),
    })

    # 2. Secondary peak if clip > 18s (separated by at least 8s)
    if duration > 18.0 and max_peaks >= 2:
        smoothed_copy = smoothed.copy()
        mask_radius = int(8.0 * effective_fps)
        mask_start = max(0, best_idx - mask_radius)
        mask_end = min(len(smoothed_copy), best_idx + mask_radius)
        smoothed_copy[mask_start:mask_end] = 0.0

        if np.max(smoothed_copy) > (peak_score * 0.35):
            second_idx = int(np.argmax(smoothed_copy))
            second_start = max(0.0, second_idx / effective_fps)
            second_end = min(duration, second_start + target_duration_s)
            segments.append({
                "source_in_ms": round(second_start * 1000.0, 2),
                "length_ms": round((second_end - second_start) * 1000.0, 2),
                "score": round(min(1.0, float(smoothed_copy[second_idx]) / 25.0), 3),
            })

            # 3. Tertiary peak if clip > 55s (separated by at least 12s from both peaks)
            if duration > 55.0 and max_peaks >= 3:
                mask_radius2 = int(12.0 * effective_fps)
                mask2_start = max(0, second_idx - mask_radius2)
                mask2_end = min(len(smoothed_copy), second_idx + mask_radius2)
                smoothed_copy[mask2_start:mask2_end] = 0.0

                if np.max(smoothed_copy) > (peak_score * 0.30):
                    third_idx = int(np.argmax(smoothed_copy))
                    third_start = max(0.0, third_idx / effective_fps)
                    third_end = min(duration, third_start + target_duration_s)
                    segments.append({
                        "source_in_ms": round(third_start * 1000.0, 2),
                        "length_ms": round((third_end - third_start) * 1000.0, 2),
                        "score": round(min(1.0, float(smoothed_copy[third_idx]) / 25.0), 3),
                    })

    # Sort segments chronologically for natural timeline order per clip
    segments.sort(key=lambda s: s["source_in_ms"])
    return segments


def scout_directory(
    directory_path: str,
    max_workers: int = 3,
    log_fn=print,
    track_name: str = "[AI SELECTS] Kiting Action",
    label_prefix: str = "[ACTION]",
    target_duration_s: float = 3.5,
    max_peaks: int = 3,
) -> List[Dict[str, Any]]:
    """Scan a directory for video files and extract peak action selects using parallel workers."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    valid_exts = {".mov", ".mp4", ".m4v", ".avi"}
    video_files = []

    for root, _, files in os.walk(directory_path):
        if "proxy" in root.lower():
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts and not f.startswith("._"):
                video_files.append(os.path.join(root, f))

    video_files.sort()
    log_fn(f"[AI Scout] Found {len(video_files)} video files in '{directory_path}' (using {max_workers} parallel workers)")

    selects = []
    completed = 0

    def process_file(fpath):
        fname = os.path.basename(fpath)
        try:
            peaks = analyze_clip_action(
                fpath,
                fps_sample=1.0,
                target_duration_s=target_duration_s,
                max_peaks=max_peaks,
            )
            clip_selects = []
            for p_idx, peak in enumerate(peaks):
                label_suffix = f" (Cut {p_idx+1})" if len(peaks) > 1 else ""
                clip_selects.append({
                    "name": f"{os.path.splitext(fname)[0]}{label_suffix}",
                    "media_path": fpath,
                    "source_in_ms": peak["source_in_ms"],
                    "length_ms": peak["length_ms"],
                    "score": peak["score"],
                    "label": f"{label_prefix} {os.path.splitext(fname)[0]}{label_suffix}",
                    "track_name": track_name,
                })
            return clip_selects, fname
        except Exception as e:
            return [], f"ERROR: {e}"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, fp): fp for fp in video_files}
        for future in as_completed(futures):
            completed += 1
            clip_results, fname = future.result()
            selects.extend(clip_results)
            if completed % 5 == 0 or completed == len(video_files):
                log_fn(f"  [AI Scout Progress] {completed}/{len(video_files)} clips scouted ({len(selects)} action cuts detected)...")

    # Sort selects by file path and source start time
    selects.sort(key=lambda s: (s["media_path"], s["source_in_ms"]))
    log_fn(f"[AI Scout] Completed '{track_name}'! Identified {len(selects)} peak action segments.")
    return selects


def scout_drone_locations(
    drone_root_path: str,
    max_workers: int = 3,
    target_duration_s: float = 3.5,
    log_fn=print,
) -> List[Dict[str, Any]]:
    """Scout all 3 drone folders and assign each to its own dedicated location track."""
    all_selects = []

    subfolders = os.listdir(drone_root_path)

    # Match folders
    dahab_dir = next((d for d in subfolders if "dahab" in d.lower()), None)
    hurghada_dir = next((d for d in subfolders if "hurghada" in d.lower()), None)
    sokhna_dir = next((d for d in subfolders if "sokhna" in d.lower()), None)

    configs = []
    if dahab_dir:
        configs.append((
            os.path.join(drone_root_path, dahab_dir),
            "[AI SELECTS] Drone - Dahab Blue Lagoon",
            "[DAHAB PROMO]",
        ))
    if hurghada_dir:
        configs.append((
            os.path.join(drone_root_path, hurghada_dir),
            "[AI SELECTS] Drone - Hurghada",
            "[HURGHADA PROMO]",
        ))
    if sokhna_dir:
        configs.append((
            os.path.join(drone_root_path, sokhna_dir),
            "[AI SELECTS] Drone - Sokhna",
            "[SOKHNA PROMO]",
        ))

    for folder_path, track_name, label_prefix in configs:
        log_fn(f"\n=======================================================")
        log_fn(f"Scouting Location: {track_name}")
        log_fn(f"Folder: {folder_path}")
        log_fn(f"=======================================================")
        loc_selects = scout_directory(
            folder_path,
            max_workers=max_workers,
            log_fn=log_fn,
            track_name=track_name,
            label_prefix=label_prefix,
            target_duration_s=target_duration_s,
            max_peaks=3,
        )
        all_selects.extend(loc_selects)

    return all_selects


def export_selects_manifest(
    selects: List[Dict[str, Any]],
    manifest_name: str = "AI Selects",
    output_path: Optional[str] = None,
    merge_existing: bool = False,
) -> str:
    """Save detected selects into a JSON manifest for VEGAS Pro and Resolve.

    When merge_existing is False, replaces with fresh cuts.
    Uses ensure_ascii=False to guarantee Unicode directory paths (e.g. drone\uf028)
    are preserved as valid UTF-8.
    """
    if not output_path:
        bridge_dir = Path.home() / ".timeline_bridge"
        bridge_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(bridge_dir / "ai_selects_manifest.json")

    combined_clips = []
    seen = set()

    if merge_existing and os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8-sig") as f:
                existing_data = json.load(f)
                for c in existing_data.get("clips", []):
                    key = (c.get("media_path"), c.get("source_in_ms"))
                    if key not in seen:
                        seen.add(key)
                        combined_clips.append(c)
        except Exception:
            combined_clips = []

    for c in selects:
        key = (c.get("media_path"), c.get("source_in_ms"))
        if key not in seen:
            seen.add(key)
            combined_clips.append(c)

    manifest = {
        "manifest_name": manifest_name,
        "track_name": "[AI SELECTS] Drone Footage",
        "clip_count": len(combined_clips),
        "clips": combined_clips,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return output_path
