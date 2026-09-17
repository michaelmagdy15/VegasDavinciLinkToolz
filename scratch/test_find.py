import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

tl = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')

def simulate_find(target_ms, hint):
    fallback = None
    matches = []
    for ti, t in enumerate(tl.get('tracks', [])):
        if not t.get('is_video'): continue
        tname = (t.get('name') or '').lower()
        if '[adjustment]' in tname or 'film burn' in tname or 'filmburn' in tname:
            continue
        for ci, c in enumerate(t.get('clips', [])):
            start = c.get('timeline_start_ms', 0)
            end = start + c.get('timeline_length_ms', 0)
            if start <= (target_ms + 200) and end >= (target_ms - 200):
                clip_name = c.get('name') or ''
                matches.append((ti, t.get('name'), clip_name, start, end, c.get('media_path')))
                if hint and hint.lower() in clip_name.lower():
                    return "HINT_MATCH", (ti, t.get('name'), clip_name, start, end, c.get('media_path'))
                if fallback is None and not c.get('mute'):
                    fallback = (ti, t.get('name'), clip_name, start, end, c.get('media_path'))
    return ("FALLBACK", fallback) if fallback else ("NONE", None)

print("Simulating FindTargetVideoEvent for all 7 targets:")
targets = [
    (13700, "9209"),
    (26400, "0013_D"),
    (32830, "0068_D"),
    (33800, "0004_D"),
    (41330, ""),
    (43830, ""),
    (47400, "8192")
]
for ms, hint in targets:
    res, ev = simulate_find(ms, hint)
    print(f"Target {ms/1000:.2f}s (hint='{hint}'): Result={res} -> {ev}")
