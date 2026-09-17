import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

print(f"{'Vegas Track':<15} | {'Mute':<5} | {'Solo':<5} | {'Composite':<10} | {'Clips':<6} | Name")
print("-" * 75)

for t in d.get('tracks', []):
    if t.get('is_video'):
        idx = t.get('index')
        name = t.get('name')
        mute = t.get('mute')
        solo = t.get('solo')
        comp = t.get('composite_mode', 'Normal')
        n_clips = len(t.get('clips', []))
        print(f"Track {idx:<9} | {str(mute):<5} | {str(solo):<5} | {str(comp):<10} | {n_clips:<6} | {name}")
