import sys, os
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')

print("All video events between 55.0s and 72.0s across ALL tracks:")
for ti, t in enumerate(d.get('tracks', [])):
    if not t.get('is_video'): continue
    tname = t.get('name', f'Track {ti}')
    for ci, ev in enumerate(t.get('events', [])):
        st = ev.get('timeline_start_ms', 0)
        dur = ev.get('timeline_length_ms', 0)
        end = st + dur
        if (st <= 72000 and end >= 55000):
            fn = os.path.basename(ev.get('media_path', ''))
            rate = ev.get('playback_rate', 1.0)
            print(f"Track {ti:2d} ('{tname:12s}'): st={st/1000:6.2f}s - {end/1000:6.2f}s (dur={dur/1000:4.2f}s) | rate={rate:.2f} | file='{fn}'")
