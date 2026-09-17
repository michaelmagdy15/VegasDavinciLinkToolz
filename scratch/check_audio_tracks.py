import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
fps = float(tl.GetSetting('timelineFrameRate'))
start_frame = tl.GetStartFrame()

print(f"Checking Audio Tracks in: {tl.GetName()}")
num_a = tl.GetTrackCount('audio')
print(f"Audio track count: {num_a}")

for a in range(1, num_a + 1):
    aname = tl.GetTrackName('audio', a)
    items = tl.GetItemListInTrack('audio', a) or []
    print(f"\nAudio Track {a} ({aname}): {len(items)} items")
    prev_end = None
    for it in items:
        s = it.GetStart()
        e = it.GetEnd()
        dur = it.GetDuration()
        name = it.GetName()
        tc_s = (s - start_frame) / fps
        tc_e = (e - start_frame) / fps
        if prev_end is not None and s > prev_end:
            gap = s - prev_end
            print(f"  GAP of {gap} frames ({gap/fps:.3f}s) before {name} at {tc_s:.2f}s")
        print(f"    Item: {name} | {tc_s:.2f}s -> {tc_e:.2f}s (dur: {dur/fps:.2f}s)")
        prev_end = e
