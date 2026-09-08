"""
ai_scout.py — Automated Motion & Visual Action Scout for Video Footage.

Analyzes video clips using hardware-accelerated FFmpeg frame sampling,
detects peak action moments (jumps, carves, kiteloops, water spray),
and generates pre-trimmed selects manifests for VEGAS Pro and DaVinci Resolve.
"""

import os
import sys
import glob
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np


def get_clip_duration_seconds(file_path: str) -> float:
    """Return video duration in seconds via ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 0.0


def analyze_clip_action(file_path: str, fps_sample: float = 2.0, target_duration_s: float = 2.5) -> List[Dict[str, Any]]:
    """Sample video at low-res to compute inter-frame visual motion delta.

    Returns a list of peak action segments (usually 1 or 2 per clip).
    Each segment contains:
        source_in_ms: Start time in milliseconds
        length_ms: Duration in milliseconds
        score: Normalized action score (0.0 to 1.0)
    """
    duration = get_clip_duration_seconds(file_path)
    if duration < 1.0:
        return []

    # If clip is already short (<= 3.5s), keep the whole clip
    if duration <= target_duration_s + 0.5:
        return [{
            "source_in_ms": 0.0,
            "length_ms": duration * 1000.0,
            "score": 0.5,
        }]

    # Fast decoding: for long clips (> 15s), decode keyframes only (10x-20x faster)
    if duration > 15.0:
        cmd = [
            "ffmpeg",
            "-v", "error",
            "-skip_frame", "nokey",
            "-i", file_path,
            "-vf", "scale=160:90,format=gray",
            "-f", "rawvideo",
            "-",
        ]
    else:
        cmd = [
            "ffmpeg",
            "-v", "error",
            "-i", file_path,
            "-vf", f"fps={fps_sample},scale=160:90,format=gray",
            "-f", "rawvideo",
            "-",
        ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        raw_bytes = proc.stdout.read()
        proc.stdout.close()
        proc.wait()
    except Exception:
        return [{
            "source_in_ms": 0.0,
            "length_ms": min(duration, target_duration_s) * 1000.0,
            "score": 0.5,
        }]

    frame_size = 90 * 160
    num_frames = len(raw_bytes) // frame_size
    if num_frames < 2:
        return [{
            "source_in_ms": 0.0,
            "length_ms": min(duration, target_duration_s) * 1000.0,
            "score": 0.5,
        }]

    # Calculate actual effective frame rate of sampled frames
    effective_fps = num_frames / duration if duration > 0 else fps_sample

    frames = np.frombuffer(raw_bytes[: num_frames * frame_size], dtype=np.uint8).reshape((num_frames, 90, 160))

    # Compute absolute difference between consecutive frames
    diffs = np.zeros(num_frames - 1, dtype=np.float32)
    for i in range(num_frames - 1):
        diffs[i] = np.mean(np.abs(frames[i + 1].astype(np.float32) - frames[i].astype(np.float32)))

    if len(diffs) == 0:
        return []

    # Moving average window over target duration
    window_frames = max(1, int(round(target_duration_s * effective_fps)))
    if len(diffs) <= window_frames:
        return [{
            "source_in_ms": 0.0,
            "length_ms": min(duration, target_duration_s) * 1000.0,
            "score": float(np.mean(diffs)),
        }]

    kernel = np.ones(window_frames) / window_frames
    smoothed = np.convolve(diffs, kernel, mode="valid")

    segments = []

    # Primary peak
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

    # If clip is longer than 25 seconds, search for a secondary peak separated by at least 8s
    if duration > 25.0:
        smoothed_copy = smoothed.copy()
        mask_radius = int(8.0 * effective_fps)
        mask_start = max(0, best_idx - mask_radius)
        mask_end = min(len(smoothed_copy), best_idx + mask_radius)
        smoothed_copy[mask_start:mask_end] = 0.0

        if np.max(smoothed_copy) > (peak_score * 0.5):
            second_idx = int(np.argmax(smoothed_copy))
            second_start = max(0.0, second_idx / effective_fps)
            second_end = min(duration, second_start + target_duration_s)
            segments.append({
                "source_in_ms": round(second_start * 1000.0, 2),
                "length_ms": round((second_end - second_start) * 1000.0, 2),
                "score": round(min(1.0, float(smoothed_copy[second_idx]) / 25.0), 3),
            })

    return segments


def scout_directory(directory_path: str, max_workers: int = 4, log_fn=print) -> List[Dict[str, Any]]:
    """Scan a directory for video files and extract peak action selects using parallel workers."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    valid_exts = {".mov", ".mp4", ".m4v", ".avi"}
    video_files = []

    for root, _, files in os.walk(directory_path):
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
            peaks = analyze_clip_action(fpath)
            clip_selects = []
            for p_idx, peak in enumerate(peaks):
                label_suffix = f" (Part {p_idx+1})" if len(peaks) > 1 else ""
                clip_selects.append({
                    "name": f"{os.path.splitext(fname)[0]}{label_suffix}",
                    "media_path": fpath,
                    "source_in_ms": peak["source_in_ms"],
                    "length_ms": peak["length_ms"],
                    "score": peak["score"],
                    "label": f"[ACTION] {os.path.splitext(fname)[0]}",
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
                log_fn(f"  [AI Scout Progress] {completed}/{len(video_files)} clips scouted ({len(selects)} action moments detected)...")


    log_fn(f"[AI Scout] Completed! Identified {len(selects)} peak action segments.")
    return selects


def export_selects_manifest(
    selects: List[Dict[str, Any]],
    manifest_name: str = "AI Selects",
    output_path: Optional[str] = None,
    merge_existing: bool = True,
) -> str:
    """Save detected selects into a JSON manifest for VEGAS Pro and Resolve.
    
    If merge_existing is True and manifest exists, appends new clips without duplicating.
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
        "track_name": "[AI SELECTS] Kiting Action",
        "clip_count": len(combined_clips),
        "clips": combined_clips,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return output_path
