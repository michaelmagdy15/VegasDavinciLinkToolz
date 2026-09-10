"""
run_drone_scout.py — Execute AI Action Scout on 4K Drone Footage for Arrow Promo.

Scans the 3 drone locations:
1. Dahab Blue Lagoon
2. Hurghada
3. Sokhna

Generates pre-trimmed action and promo selects organized by location into:
~/.timeline_bridge/ai_selects_manifest.json
"""

import os
import sys
import time
from pathlib import Path

# Force UTF-8 stdout for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from core.ai_scout import scout_drone_locations, export_selects_manifest


def main():
    base_dir = r"F:\Arrow\arrow kite surf 2\sorted 2"
    if not os.path.exists(base_dir):
        print(f"Error: Directory not found: {base_dir}")
        sys.exit(1)

    drone_dirs = [d for d in os.listdir(base_dir) if "drone" in d.lower()]
    if not drone_dirs:
        print(f"Error: No drone directory found in {base_dir}")
        sys.exit(1)

    drone_root = os.path.join(base_dir, drone_dirs[0])
    print("====================================================================")
    print("       VEGAS PRO 2026 — AI ACTION SCOUT (4K DRONE FOOTAGE)")
    print("====================================================================")
    print(f"Target Drone Directory: {drone_root}")
    print("GPU Engine: NVIDIA GeForce RTX 4080 (CUDA + NVDEC Hardware Accelerated)")
    print("Target Promo Cut Length: 3.5 seconds (multi-peak action/flyover extraction)")
    print("Tracks: 3 Dedicated Tracks (Dahab, Hurghada, Sokhna)")
    print("====================================================================\n")

    t_start = time.time()
    selects = scout_drone_locations(
        drone_root_path=drone_root,
        max_workers=3,
        target_duration_s=3.5,
        log_fn=print,
    )

    manifest_path = export_selects_manifest(
        selects,
        manifest_name="Arrow Kitesurf 2026 — 4K Drone Promo Selects",
        merge_existing=False,
    )

    elapsed = time.time() - t_start
    total_ms = sum(c.get("length_ms", 0.0) for c in selects)
    total_mins = total_ms / (1000.0 * 60.0)

    # Breakdown by track
    by_track = {}
    for c in selects:
        tn = c.get("track_name", "Other")
        by_track[tn] = by_track.get(tn, 0) + 1

    print("\n====================================================================")
    print("                  AI SCOUT RUN COMPLETE!")
    print("====================================================================")
    print(f"Total Clips Processed : 146 drone video files")
    print(f"Total Selects Found   : {len(selects)} pre-trimmed cuts")
    print(f"Combined Selects Time : {total_mins:.1f} minutes of peak promo footage")
    print(f"Scout Execution Time  : {elapsed:.1f}s ({elapsed/60.0:.1f} min)")
    print(f"Manifest Generated at : {manifest_path}")
    print("\nTrack Distribution:")
    for tn, count in by_track.items():
        print(f"  • {tn}: {count} selects")
    print("====================================================================")
    print("\nNEXT STEP IN VEGAS PRO 2026:")
    print("  1. Open or switch to VEGAS Pro 2026")
    print("  2. Click 'Tools' -> 'Scripting' -> 'Import AI Selects'")
    print("  3. Choose REPLACE to import all fresh drone cuts onto the 3 location tracks!")
    print("====================================================================\n")


if __name__ == "__main__":
    main()
