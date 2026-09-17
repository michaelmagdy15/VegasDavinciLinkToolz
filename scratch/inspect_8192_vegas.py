import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

for t in d.get('tracks', []):
    for c in t.get('clips', []):
        if '8192' in c.get('name', ''):
            print(f"Track {t.get('index')} ({t.get('name')}):")
            print(f"  Track motion: {t.get('track_motion')}")
            for k in ['name', 'zoom_x', 'zoom_y', 'pan_x', 'pan_y', 'rotation_angle', 'motion_keyframes']:
                print(f"  Clip {k}: {c.get(k)}")
