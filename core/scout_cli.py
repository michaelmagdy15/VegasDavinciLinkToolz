"""
core/scout_cli.py — Streaming JSON CLI Bridge for WinUI 3 / Desktop GUI.

Runs the AI Action Scout and streams real-time JSON events to stdout
with instant flushing so GUI clients can render 60fps progress bars,
display live clip names, and populate results tables.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from core.ai_scout import (
    scout_directory,
    scout_drone_locations,
    export_selects_manifest,
    analyze_clip_action,
)


def emit_event(event_type: str, **kwargs):
    """Emit a JSON event line to stdout and flush immediately."""
    payload = {"event": event_type, **kwargs}
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def run_scout(
    folder_path: str,
    target_duration: float = 3.5,
    max_peaks: int = 3,
    track_mode: str = "location",
    max_workers: int = 3,
    output_manifest: str = "",
):
    if not os.path.exists(folder_path):
        emit_event("error", message=f"Directory not found: {folder_path}")
        return 1

    # Check for subfolders
    subdirs = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d)) and not d.startswith(".")]
    
    # Collect all video files
    valid_exts = {".mov", ".mp4", ".m4v", ".avi"}
    all_videos = []
    for root, _, files in os.walk(folder_path):
        if "proxy" in root.lower():
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts and not f.startswith("._"):
                all_videos.append(os.path.join(root, f))

    all_videos.sort()
    total_files = len(all_videos)

    emit_event(
        "start",
        folder=folder_path,
        total_files=total_files,
        subfolders=subdirs,
        target_duration=target_duration,
        max_peaks=max_peaks,
        track_mode=track_mode,
    )

    if total_files == 0:
        emit_event("complete", total_cuts=0, manifest_path="", message="No video files found in folder.")
        return 0

    t_start = time.time()
    all_selects = []
    completed_files = 0

    # Build folder-to-track mapping
    def get_track_info(fpath):
        rel = os.path.relpath(fpath, folder_path)
        parts = rel.split(os.sep)
        if len(parts) > 1 and track_mode == "location":
            sub_name = parts[0]
            # Clean up display name
            clean_sub = "".join(c for c in sub_name if ord(c) < 128 or c.isalnum()).strip()
            return f"[AI SELECTS] {clean_sub}", f"[{clean_sub.upper()}]"
        return "[AI SELECTS] Highlights", "[PROMO]"

    # Process files sequentially or with threadpool
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_single(fp):
        fname = os.path.basename(fp)
        track_name, label_prefix = get_track_info(fp)
        try:
            peaks = analyze_clip_action(
                fp,
                fps_sample=1.0,
                target_duration_s=target_duration,
                max_peaks=max_peaks,
            )
            clip_cuts = []
            for p_idx, peak in enumerate(peaks):
                label_suffix = f" (Cut {p_idx+1})" if len(peaks) > 1 else ""
                clip_cuts.append({
                    "name": f"{os.path.splitext(fname)[0]}{label_suffix}",
                    "media_path": fp,
                    "source_in_ms": peak["source_in_ms"],
                    "length_ms": peak["length_ms"],
                    "score": peak["score"],
                    "label": f"{label_prefix} {os.path.splitext(fname)[0]}{label_suffix}",
                    "track_name": track_name,
                })
            return clip_cuts, fname
        except Exception as e:
            return [], f"ERROR: {e}"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(process_single, fp): fp for fp in all_videos}
        for future in as_completed(future_map):
            completed_files += 1
            cuts, fname = future.result()
            all_selects.extend(cuts)

            # Emit progress update
            emit_event(
                "progress",
                current=completed_files,
                total=total_files,
                current_file=fname,
                cuts_found=len(all_selects),
                percent=round((completed_files / total_files) * 100, 1),
            )

            # Emit individual cuts for live gallery update
            for c in cuts:
                emit_event("cut_found", cut=c)

    # Sort selects
    all_selects.sort(key=lambda s: (s["track_name"], s["media_path"], s["source_in_ms"]))

    # Export manifest
    out_path = output_manifest if output_manifest else None
    saved_path = export_selects_manifest(
        all_selects,
        manifest_name="AI Video Culling Selects",
        output_path=out_path,
        merge_existing=False,
    )

    elapsed = time.time() - t_start
    total_ms = sum(c.get("length_ms", 0.0) for c in all_selects)

    emit_event(
        "complete",
        total_files=total_files,
        total_cuts=len(all_selects),
        total_duration_minutes=round(total_ms / (1000.0 * 60.0), 2),
        elapsed_seconds=round(elapsed, 1),
        manifest_path=saved_path,
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description="AI Video Culling CLI Bridge")
    parser.add_argument("--folder", required=True, help="Footage folder to scout")
    parser.add_argument("--target-duration", type=float, default=3.5, help="Target cut length in seconds")
    parser.add_argument("--max-peaks", type=int, default=3, help="Max cuts to extract per long take")
    parser.add_argument("--track-mode", choices=["location", "single"], default="location", help="Track layout mode")
    parser.add_argument("--max-workers", type=int, default=3, help="Worker threads")
    parser.add_argument("--output-manifest", default="", help="Custom output manifest path")

    args = parser.parse_args()
    return run_scout(
        folder_path=args.folder,
        target_duration=args.target_duration,
        max_peaks=args.max_peaks,
        track_mode=args.track_mode,
        max_workers=args.max_workers,
        output_manifest=args.output_manifest,
    )


if __name__ == "__main__":
    sys.exit(main())
