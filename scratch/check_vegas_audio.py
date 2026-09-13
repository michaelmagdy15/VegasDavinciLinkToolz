import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"c:\Users\Mi5a\VegasDavinciLinkTool")
from core.live_bridge import load_manifest_json

tl = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')
print("=== AUDIO TRACKS IN VEGAS TIMELINE JSON ===")
for t in tl.get('tracks', []):
    if t.get('is_audio'):
        idx = t.get('index')
        name = t.get('name')
        vol = t.get('volume_db', 0.0)
        pan = t.get('pan', 0.0)
        fxs = [f.get('name') for f in t.get('effects', [])]
        clips = len(t.get('clips', []))
        print(f"VEGAS Audio Track #{idx} '{name}': {clips} clips | Vol: {vol} dB | Pan: {pan} | FX: {fxs}")
