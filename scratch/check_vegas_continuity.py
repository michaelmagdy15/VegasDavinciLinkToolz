import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

# Check VEGAS tracks
active_tracks = []
for t in d.get('tracks', []):
    if t.get('is_video', True) and not t.get('mute'):
        name = t.get('name', '')
        if 'burn' not in name.lower() and 'light' not in name.lower() and t.get('composite_mode') != 'Screen':
            active_tracks.append(t)

print(f"Active base video tracks in VEGAS: {len(active_tracks)}")

# Check frame by frame from 0 to 63 seconds (at 29.97 fps, 0 to 1890 frames)
vegas_fps = float(d.get('frame_rate', 29.97))
total_frames = int(63.0 * vegas_fps)

covered_frames = [False] * total_frames
for t in active_tracks:
    for c in t.get('clips', []):
        if c.get('mute'): continue
        s_ms = c.get('timeline_start_ms')
        l_ms = c.get('timeline_length_ms')
        s_f = int(round((s_ms / 1000.0) * vegas_fps))
        e_f = int(round(((s_ms + l_ms) / 1000.0) * vegas_fps))
        for f in range(max(0, s_f), min(total_frames, e_f)):
            covered_frames[f] = True

gap_ranges = []
in_gap = False
gap_start = 0
for f in range(total_frames):
    if not covered_frames[f] and not in_gap:
        in_gap = True
        gap_start = f
    elif covered_frames[f] and in_gap:
        in_gap = False
        gap_ranges.append((gap_start, f, f - gap_start))

if in_gap:
    gap_ranges.append((gap_start, total_frames, total_frames - gap_start))

print(f"Gaps in VEGAS 0-63s (at {vegas_fps} fps): {len(gap_ranges)}")
for gs, ge, gcount in gap_ranges:
    print(f"  Gap: frame {gs} -> {ge} ({gcount} frames, {gcount/vegas_fps*1000:.1f}ms / {gcount/vegas_fps:.2f}s)")
