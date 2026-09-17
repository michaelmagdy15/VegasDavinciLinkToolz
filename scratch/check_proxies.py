import json
import os
from pathlib import Path
import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

json_path = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
data = load_manifest_json(str(json_path))

media_paths = set()
for t in data.get('tracks', []):
    for c in t.get('clips', []):
        mp = c.get('media_path')
        if mp:
            media_paths.add(mp)

print(f"Total unique media paths on timeline: {len(media_paths)}")
proxy_paths = [mp for mp in media_paths if 'proxy' in mp.lower()]
print(f"Paths with 'proxy' in path: {len(proxy_paths)}")

for p in list(proxy_paths)[:15]:
    print(" Proxy path sample:", p)
