import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app, load_manifest_json
from pathlib import Path

# 1. Load VEGAS timeline
p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

print("=== VEGAS TIMELINE AUDIT ===")
total_vegas_clips = 0
vegas_events = []

for t in d.get('tracks', []):
    if not t.get('is_video', True) or t.get('mute'):
        continue
    ti = t.get('index')
    tn = t.get('name')
    is_overlay = ('burn' in tn.lower() or 'light' in tn.lower() or 'lut' in tn.lower() or t.get('composite_mode') == 'Screen')
    for c in t.get('clips', []):
        if c.get('mute'): continue
        s = c.get('timeline_start_ms')
        l = c.get('timeline_length_ms')
        e = s + l
        vegas_events.append({
            'start': s, 'end': e, 'len': l,
            'track_idx': ti, 'track_name': tn,
            'is_overlay': is_overlay,
            'clip_name': c.get('name'),
            'playback_rate': c.get('playback_rate'),
            'fade_in_ms': c.get('fade_in_ms'),
            'fade_out_ms': c.get('fade_out_ms'),
            'raw': c
        })

print(f"Active unmuted VEGAS video events: {len(vegas_events)}")

# Sort by start
vegas_events.sort(key=lambda x: x['start'])

# Find timeline span
if vegas_events:
    total_dur_ms = max(x['end'] for x in vegas_events)
    print(f"Total VEGAS visual duration: {total_dur_ms:.1f}ms ({total_dur_ms/1000:.2f}s)")

# Check if there are any visual gaps in VEGAS (considering only base/non-overlay clips)
base_events = [e for e in vegas_events if not e['is_overlay']]
base_events.sort(key=lambda x: x['start'])

gaps = []
curr_covered = 0.0
for ev in base_events:
    if ev['start'] > curr_covered + 10.0: # gap larger than 10ms (~1/3 frame)
        gaps.append((curr_covered, ev['start'], ev['start'] - curr_covered))
    curr_covered = max(curr_covered, ev['end'])

print(f"\nVisual gaps in VEGAS base timeline: {len(gaps)}")
for gs, ge, gd in gaps:
    print(f"  GAP in VEGAS: {gs:.1f}ms -> {ge:.1f}ms (duration {gd:.1f}ms / {gd/1000:.2f}s)")

# 2. Check Resolve Timeline
resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
fps = float(tl.GetSetting('timelineFrameRate') or 24.0)
start_frame = tl.GetStartFrame()
print(f"\n=== RESOLVE TIMELINE AUDIT (FPS={fps}, StartFrame={start_frame}) ===")

resolve_items = []
for t_idx in range(tl.GetTrackCount('video'), 0, -1):
    t_name = tl.GetTrackName('video', t_idx)
    # Check if track is overlay or disabled
    # Note: V4 is disabled, V24 and V27 are overlays
    is_overlay = ('burn' in t_name.lower() or 'light' in t_name.lower() or t_idx in [24, 27, 4])
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        s = it.GetStart()
        e = it.GetEnd()
        resolve_items.append({
            'start_f': s, 'end_f': e, 'dur_f': e - s,
            'start_ms': (s - start_frame) * 1000.0 / fps,
            'end_ms': (e - start_frame) * 1000.0 / fps,
            'track_idx': t_idx, 'track_name': t_name,
            'is_overlay': is_overlay,
            'name': it.GetName(),
            'item': it
        })

resolve_base = [it for it in resolve_items if not it['is_overlay']]
resolve_base.sort(key=lambda x: x['start_f'])

r_gaps = []
curr_r_cov = start_frame
for it in resolve_base:
    if it['start_f'] > curr_r_cov:
        gap_frames = it['start_f'] - curr_r_cov
        gap_ms = (gap_frames / fps) * 1000.0
        r_gaps.append((curr_r_cov, it['start_f'], gap_frames, gap_ms))
    curr_r_cov = max(curr_r_cov, it['end_f'])

print(f"Visual gaps in Resolve base timeline: {len(r_gaps)}")
for gs, ge, gf, gms in r_gaps:
    print(f"  GAP in Resolve: frame {gs} -> {ge} ({gf} frames, {gms:.1f}ms / {gms/1000:.2f}s)")
