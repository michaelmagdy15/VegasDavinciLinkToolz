import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

data = json.load(open(r"C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json", "r", encoding="utf-8-sig"))

print(f"Project: {data.get('project_name')} | {data.get('width')}x{data.get('height')} @ {data.get('frame_rate')} fps")
print("=" * 80)

for t in data["tracks"]:
    for c in t.get("clips", []):
        start = float(c.get("timeline_start_ms", 0.0))
        length = float(c.get("timeline_length_ms", 0.0))
        if start < 100:  # Active at frame 0
            print(f"Track: {t.get('name')} (is_video={t.get('is_video')})")
            print(f"  Clip: {c.get('name')}")
            print(f"  Media: {c.get('media_path')}")
            print(f"  Start: {start}ms, Length: {length}ms, In: {c.get('source_in_ms')}ms")
            print(f"  PlaybackRate: {c.get('playback_rate')}")
            print(f"  ZoomX: {c.get('zoom_x')}, ZoomY: {c.get('zoom_y')}")
            print(f"  PanX: {c.get('pan_x')}, PanY: {c.get('pan_y')}")
            print(f"  Rotation: {c.get('rotation_angle')}")
            print("-" * 40)
