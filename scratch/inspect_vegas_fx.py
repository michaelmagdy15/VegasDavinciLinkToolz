import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')

print("=== TRACK EFFECTS & LOOKS IN VEGAS ===")
for t in d.get('tracks', []):
    fxs = t.get('effects', [])
    if fxs:
        print(f"Track '{t.get('name')}' effects:")
        for fx in fxs:
            print(f"  - {fx.get('name')} (preset: {fx.get('preset')})")
            for p in fx.get('parameters', []):
                if p.get('value'):
                    print(f"      {p.get('name')}: {p.get('value')}")

print("\n=== CLIP EFFECTS IN VEGAS (Sample of unique effects) ===")
unique_clip_fx = set()
for t in d.get('tracks', []):
    for c in t.get('clips', []):
        for fx in c.get('effects', []):
            unique_clip_fx.add((fx.get('name'), fx.get('preset')))

for name, preset in sorted(unique_clip_fx):
    print(f"  - {name} | Preset: {preset}")
