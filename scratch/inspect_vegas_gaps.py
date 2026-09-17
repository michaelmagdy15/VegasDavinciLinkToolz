import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

m = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')
tracks = m.get('tracks', [])

print("=== VEGAS PRO MANIFEST TRACK INSPECTION ===")
for i, t in enumerate(tracks):
    tname = t.get('name')
    clips = t.get('clips', [])
    if not clips:
        continue
    is_v = t.get('is_video')
    mute = t.get('mute', False)
    print(f"Track {i+1} ({'Video' if is_v else 'Audio'}) '{tname}': {len(clips)} clips | Mute: {mute}")
    prev_end = None
    for c in clips:
        s = c.get('timeline_start_ms', 0)
        l = c.get('timeline_length_ms', 0)
        e = s + l
        if prev_end is not None and s > prev_end:
            gap_ms = s - prev_end
            if gap_ms > 100: # gap > 100ms
                print(f"   Gap of {gap_ms:.0f}ms ({gap_ms/1000:.2f}s) between clips on this track before {c.get('name')} at {s/1000:.2f}s")
        prev_end = e
