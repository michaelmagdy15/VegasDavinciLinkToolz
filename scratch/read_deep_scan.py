import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')
print(f"Project: {d.get('project_name')}")
print(f"Total tracks: {len(d.get('tracks', []))}")

targets = [13700, 26400, 32830, 33800, 41330, 43830, 47400]

for target in targets:
    print(f"\n================ Target: {target/1000:.2f}s ({target}ms) ================")
    for ti, t in enumerate(d.get('tracks', [])):
        if not t.get('is_video'): continue
        tname = t.get('name', f'Track {ti}')
        for ci, ev in enumerate(t.get('events', [])):
            st = ev.get('timeline_start_ms', 0)
            dur = ev.get('timeline_length_ms', 0)
            end = st + dur
            if (st <= (target + 500) and end >= (target - 500)) or abs(st - target) < 1000:
                fn = str(ev.get('media_path')).encode('ascii', errors='replace').decode()
                cname = str(ev.get('name')).encode('ascii', errors='replace').decode()
                print(f"Track {ti} ('{tname}'): st={st:.1f}ms end={end:.1f}ms ({st/1000:.2f}s-{end/1000:.2f}s) name='{cname}' file='{fn}'")
