import sys
sys.path.insert(0, '.')
from pathlib import Path
from core.live_bridge import load_manifest_json

json_path = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
data = load_manifest_json(str(json_path))

print("=== TRACKS & FX AUDIT ===")
found_fx = []
for idx, t in enumerate(data.get('tracks', [])):
    name = t.get('name', '')
    is_v = t.get('is_video', False)
    fx = [e.get('name') for e in t.get('effects', [])]
    if is_v:
        print(f"Track #{idx} [{name}]: FX={fx}")
    for c in t.get('clips', []):
        cfx = [e.get('name') for e in c.get('effects', [])]
        if cfx:
            found_fx.append((c.get('name'), cfx))

print(f"\nTotal clips with Event/Take FX: {len(found_fx)}")
for cname, cfx in found_fx[:10]:
    print(f"  Clip '{cname}': {cfx}")
