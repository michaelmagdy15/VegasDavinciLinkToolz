import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')

replacements = [
    (13700, "9209", "Dynamic Kite Pumping (A7S)"),
    (26400, "0013_D", "Balanced Golden Hour Drone (DJI)"),
    (32830, "0068_D", "Dahab Turquoise Lagoon (DJI)"),
    (33800, "0004_D", "Low-Water Twin-Tip Chase (DJI)"),
    (41330, "9212", "Hurghada Board-Off Jump (A7 IV)"),
    (43830, "9231", "Clean Landed Kiteloop (A7S)"),
    (47400, "9382", "Explosive Water Spray at Lens (A7S 60fps)")
]

def find_event(target_ms, hint):
    fallback = None
    for ti, t in enumerate(d.get('tracks', [])):
        if not t.get('is_video'): continue
        tname = (t.get('name') or '').lower()
        if any(bad in tname for bad in ['[adjustment]', 'film burn', 'filmburn', 'halation', 'lut', 'transiotions', 'transition']):
            continue
        for ev in t.get('events', []):
            mpath = ev.get('media_path', '')
            if not mpath: continue  # Skip generated / empty clips
            st = ev.get('timeline_start_ms', 0)
            end = st + ev.get('timeline_length_ms', 0)
            if st <= (target_ms + 300) and end >= (target_ms - 300):
                cname = ev.get('name', '')
                if hint and (hint.lower() in cname.lower() or hint.lower() in mpath.lower()):
                    return (ti, t.get('name'), cname, st, end, mpath)
                if fallback is None and not ev.get('mute'):
                    fallback = (ti, t.get('name'), cname, st, end, mpath)
    return fallback

print("Testing exact match on deep scan for all 7 replacements:")
for ms, hint, title in replacements:
    match = find_event(ms, hint)
    if match:
        print(f"SUCCESS: {ms/1000:.1f}s [{title}] -> Track {match[0]} ('{match[1]}'), Clip='{match[2]}', st={match[3]:.1f}ms, end={match[4]:.1f}ms")
    else:
        print(f"FAILED to find match for {ms/1000:.1f}s [{title}]")
