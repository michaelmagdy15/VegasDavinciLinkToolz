import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

tl = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')

targets = [13700, 26400, 32830, 33800, 41330, 43830, 47400]

for target in targets:
    print(f"\n================ Target: {target/1000:.2f}s ({target}ms) ================")
    for ti, t in enumerate(tl.get('tracks', [])):
        if not t.get('is_video'): continue
        tname = t.get('name', f'Track {ti}')
        for ci, c in enumerate(t.get('clips', [])):
            st = c.get('timeline_start_ms', 0)
            dur = c.get('timeline_length_ms', 0)
            end = st + dur
            if (st <= (target + 500) and end >= (target - 500)) or abs(st - target) < 1000:
                fn = str(c.get('media_path')).encode('ascii', errors='replace').decode()
                cname = str(c.get('name')).encode('ascii', errors='replace').decode()
                print(f"Track {ti} ('{tname}'): st={st:.1f}ms end={end:.1f}ms ({st/1000:.2f}s-{end/1000:.2f}s) name='{cname}' file='{fn}'")
