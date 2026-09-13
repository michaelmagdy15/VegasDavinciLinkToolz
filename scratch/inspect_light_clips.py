import sys
sys.path.insert(0, r"c:\Users\Mi5a\VegasDavinciLinkTool")
from core.live_bridge import load_manifest_json

tl = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')
for t in tl.get('tracks', []):
    for c in t.get('clips', []):
        name = c.get('name', '')
        if 'LIGHT' in name:
            tidx = t.get('index')
            s = c.get('timeline_start_ms')
            l = c.get('timeline_length_ms')
            i = c.get('source_in_ms')
            r = c.get('playback_rate')
            print(f"Track {tidx}: {name} | start={s} | len={l} | in={i} | rate={r}")
