import sys, os
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')

for ti, t in enumerate(d.get('tracks', [])):
    if not t.get('is_video'): continue
    for ci, ev in enumerate(t.get('events', [])):
        mpath = ev.get('media_path', '')
        if '9235' in mpath or '9318' in mpath:
            st = ev.get('timeline_start_ms', 0)
            dur = ev.get('timeline_length_ms', 0)
            end = st + dur
            print(f"Track {ti} ({t.get('name')}): {os.path.basename(mpath)} | st={st/1000:.2f}s end={end/1000:.2f}s (dur={dur/1000:.2f}s) rate={ev.get('playback_rate')}")
