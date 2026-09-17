import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

zero_count = 0
non_zero_count = 0
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        px = it.GetProperty('Pan')
        py = it.GetProperty('Tilt')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        if abs(px) < 0.01 and abs(py) < 0.01 and abs(zx - 1.0) < 0.01 and abs(zy - 1.0) < 0.01:
            zero_count += 1
        else:
            non_zero_count += 1

print(f"Normal clips (Pan=0, Tilt=0, Zoom=1.0): {zero_count}")
print(f"Clips with non-default transforms: {non_zero_count}")
