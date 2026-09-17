import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app, load_manifest_json

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
fps = float(tl.GetSetting('timelineFrameRate'))
start_frame = tl.GetStartFrame()

# Check clips in Resolve timeline
items_after_65 = []
for t in range(1, tl.GetTrackCount('video') + 1):
    tname = tl.GetTrackName('video', t)
    for it in tl.GetItemListInTrack('video', t) or []:
        s = it.GetStart()
        e = it.GetEnd()
        tc_s = (s - start_frame) / fps
        if tc_s > 64.0:
            items_after_65.append((tc_s, (e - start_frame) / fps, tname, it.GetName()))

items_after_65.sort()
print(f"Total clips after 64s in Resolve: {len(items_after_65)}")
for s, e, tn, cn in items_after_65:
    print(f"  [{tn}] {cn}: {s:.2f}s -> {e:.2f}s (dur: {e-s:.2f}s)")
