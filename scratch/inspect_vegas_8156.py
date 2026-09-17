import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

for t in d.get('tracks', []):
    for c in t.get('clips', []):
        if '8156' in c.get('name', '') or '8156' in c.get('media_path', ''):
            print(f"Track {t.get('index')} ({t.get('name')}):")
            for k in ['name', 'timeline_start_ms', 'timeline_length_ms', 'fade_in_ms', 'fade_out_ms', 'fade_gain', 'effects', 'mute']:
                print(f"  {k}: {c.get(k)}")
