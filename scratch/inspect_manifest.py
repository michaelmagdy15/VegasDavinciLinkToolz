import sys
sys.path.insert(0, r"c:\Users\Mi5a\VegasDavinciLinkTool")
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

print("=== ALL MARKERS ===")
for m in d.get('markers', []):
    pos = m.get('position_ms', 0)
    print(f"Marker {m.get('index')}: '{m.get('name')}' at {pos}ms ({pos/1000.0:.2f}s) tc={m.get('timecode')}")

print("\n=== CLIPS AT 38s - 48s ===")
for t in d.get('tracks', []):
    tm = t.get('track_motion')
    if tm:
        print(f"Track {t.get('index')}: '{t.get('name')}' -> track_motion: {tm}")
    else:
        print(f"Track {t.get('index')}: '{t.get('name')}' (no track_motion)")
