import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app, load_manifest_json
from pathlib import Path

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

d = load_manifest_json(str(Path.home() / '.timeline_bridge' / 'vegas_timeline.json'))

print("=== VEGAS: First 5 seconds of video clips (ordered by start time) ===")
v_clips = []
for t in d.get('tracks', []):
    if not t.get('is_video', True): continue
    for c in t.get('clips', []):
        if c.get('timeline_start_ms') < 5000:
            v_clips.append((c.get('timeline_start_ms'), c.get('timeline_length_ms'), t.get('index'), t.get('name'), t.get('mute'), c.get('name')))

v_clips.sort(key=lambda x: x[0])
for s, l, ti, tn, tm, cn in v_clips:
    print(f"  [{s:6.1f}ms -> {s+l:6.1f}ms] (dur {l:5.1f}ms) | Track {ti:2d} ({tn:12s}, mute={tm}) | {cn}")

print("\n=== RESOLVE: First 5 seconds (frames 86400 -> 86520, ordered by start frame) ===")
r_clips = []
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        if it.GetStart() < 86520:
            r_clips.append((it.GetStart(), it.GetEnd(), t_idx, tl.GetTrackName('video', t_idx), it.GetName()))

r_clips.sort(key=lambda x: (x[0], x[2]))
for s, e, ti, tn, cn in r_clips:
    print(f"  [frame {s:5d} -> {e:5d}] (dur {e-s:3d}f = {(e-s)/24:.2f}s) | V{ti:2d} ({tn:12s}) | {cn}")
