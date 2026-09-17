import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
fps = float(tl.GetSetting('timelineFrameRate'))
start_frame = tl.GetStartFrame()

print("Clips in the first 10 seconds (01:00:00:00 - 01:00:10:00):")
for t in range(tl.GetTrackCount('video'), 0, -1):
    tname = tl.GetTrackName('video', t)
    for it in tl.GetItemListInTrack('video', t) or []:
        s = it.GetStart()
        e = it.GetEnd()
        tc_s = (s - start_frame) / fps
        tc_e = (e - start_frame) / fps
        if tc_s < 10.0:
            print(f"  Track V{t} ('{tname}'): {it.GetName()} | {tc_s:.2f}s -> {tc_e:.2f}s (frames {s}..{e})")
