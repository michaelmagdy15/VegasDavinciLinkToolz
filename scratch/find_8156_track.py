import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

for t in d.get('tracks', []):
    for c in t.get('clips', []):
        if '8156' in c.get('name', '') or '8156' in c.get('file_path', ''):
            print(f"Clip 8156 is on Track {t.get('index')}: '{t.get('name')}'")
            print(f"  Track Motion: {t.get('track_motion')}")
            print(f"  Clip: {c.get('name')}")
            print(f"  Start: {c.get('start_time_ms')}ms")
