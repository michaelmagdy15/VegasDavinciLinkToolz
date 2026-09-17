import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

print(f"Total VEGAS tracks: {len(d.get('tracks', []))}")
for t in d.get('tracks', []):
    clips = t.get('clips', [])
    print(f"VEGAS Track {t.get('index'):2d} ({t.get('type')}): name='{t.get('name')}', mute={t.get('mute')}, solo={t.get('solo')}, comp_mode='{t.get('composite_mode')}', comp_lvl={t.get('composite_level')}, clips={len(clips)}")
