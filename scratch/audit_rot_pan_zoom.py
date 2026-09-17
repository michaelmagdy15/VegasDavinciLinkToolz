import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print(f"{'Track':<6} | {'Start':<6} | {'Rot':<5} | {'Pan':<14} | {'Zoom':<10} | Name")
print("-" * 80)
for t_idx in range(tl.GetTrackCount('video'), 0, -1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        name = it.GetName()
        rot = it.GetProperty('RotationAngle')
        px = it.GetProperty('Pan')
        py = it.GetProperty('Tilt')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        if rot != 0.0 or abs(px) > 1.0 or abs(py) > 1.0 or abs(zx - 1.0) > 0.05:
            print(f"V{t_idx:<5} | {it.GetStart():<6} | {rot:<5} | ({px:5.1f}, {py:5.1f}) | ({zx:.2f}, {zy:.2f}) | {name}")
