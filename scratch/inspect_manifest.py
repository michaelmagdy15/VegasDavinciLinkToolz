import json
import os
from pathlib import Path

json_path = r"C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json"
with open(json_path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

print("Project Name:", data.get("project_name"))
print("FPS:", data.get("frame_rate"))
print("Tracks count:", len(data.get("tracks", [])))
for i, t in enumerate(data.get("tracks", [])):
    print(f"Track {i+1:2d}: {t.get('name', 'unnamed'):35s} | video={str(t.get('is_video')):5s} | clips={len(t.get('clips', []))}")
