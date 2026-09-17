import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
fps = float(tl.GetSetting('timelineFrameRate'))
start_frame = tl.GetStartFrame()

print(f"Timeline: {tl.GetName()} ({fps} fps, Start: {start_frame})")

# We want to trace from frame start_frame up to frame start_frame + int(64 * fps)
# Across all video tracks, which item is visible at each frame?
# In Resolve, higher track index (e.g. V31) is on top of lower track index (e.g. V1).
# Except muted tracks! Track 4 'pick 5' was muted.
num_tracks = tl.GetTrackCount('video')

clips_by_track = {}
for t in range(1, num_tracks + 1):
    tname = tl.GetTrackName('video', t)
    # Check if enabled
    # We can check if items exist
    items = tl.GetItemListInTrack('video', t) or []
    clips_by_track[t] = (tname, items)

max_frame = start_frame + int(65 * fps)

# Find top visible item at each frame
gaps = []
in_gap = False
gap_start = None

# We can sample every frame from start_frame to max_frame
for f in range(start_frame, max_frame):
    # Check tracks from top (V_max) down to V1
    found = False
    for t in range(num_tracks, 0, -1):
        tname, items = clips_by_track[t]
        if 'pick 5' in tname.lower():
            continue
        # Check if any item covers frame f
        for it in items:
            if it.GetStart() <= f < it.GetEnd():
                found = True
                break
        if found:
            break
    
    if not found:
        if not in_gap:
            in_gap = True
            gap_start = f
    else:
        if in_gap:
            in_gap = False
            gaps.append((gap_start, f))

if in_gap:
    gaps.append((gap_start, max_frame))

print(f"Gaps found in playback (0 to 65s): {len(gaps)}")
for gs, ge in gaps:
    print(f"  GAP from frame {gs} to {ge} (duration: {ge-gs} frames, {(ge-gs)/fps*1000:.1f}ms) at TC { (gs-start_frame)/fps:.2f}s")
