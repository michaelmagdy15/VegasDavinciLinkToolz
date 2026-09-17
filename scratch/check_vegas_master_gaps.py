import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

m = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')

# Collect all video intervals from VEGAS
v_intervals = []
for t in m.get('tracks', []):
    if not t.get('is_video'):
        continue
    if t.get('mute'):
        continue
    tname = (t.get('name') or '').lower()
    # If it's not an overlay or mute
    for c in t.get('clips', []):
        s = c.get('timeline_start_ms', 0)
        l = c.get('timeline_length_ms', 0)
        v_intervals.append((s, s + l, t.get('name'), c.get('name')))

events = []
for s, e, tn, cn in v_intervals:
    events.append((s, 1))
    events.append((e, -1))
events.sort(key=lambda x: (x[0], -x[1]))

active = 0
prev = 0
vegas_gaps = []
for t, ch in events:
    if active == 0 and t > prev and prev >= 0:
        vegas_gaps.append((prev, t))
    active += ch
    prev = t

print("=== VEGAS PRO MASTER VIDEO PLAYBACK GAPS ===")
promo_gaps = [g for g in vegas_gaps if g[0] < 65000]
print(f"Total gaps in VEGAS Pro master video (0 to 65s): {len(promo_gaps)}")
for gs, ge in promo_gaps:
    print(f"  Gap: {gs/1000:.3f}s to {ge/1000:.3f}s (dur: {ge-gs:.1f}ms)")

print(f"\nGaps after 65s in VEGAS Pro: {len(vegas_gaps) - len(promo_gaps)}")
for gs, ge in [g for g in vegas_gaps if g[0] >= 65000]:
    print(f"  Gap: {gs/1000:.3f}s to {ge/1000:.3f}s (dur: {(ge-gs)/1000:.2f}s)")
