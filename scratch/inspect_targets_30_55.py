import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

tl = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')

print("All video clips between 30.0s and 55.0s across ALL tracks:")
for ti, t in enumerate(tl.get('tracks', [])):
    if not t.get('is_video'): continue
    tname = t.get('name', f'Track {ti}')
    for ci, c in enumerate(t.get('clips', [])):
        st = c.get('timeline_start_ms', 0)
        dur = c.get('timeline_length_ms', 0)
        end = st + dur
        if (st <= 55000 and end >= 30000):
            fn = str(c.get('media_path')).encode('ascii', errors='replace').decode()
            cname = str(c.get('name')).encode('ascii', errors='replace').decode()
            print(f"Track {ti} ('{tname}'): st={st/1000:.2f}s to end={end/1000:.2f}s | clip='{cname}'")
