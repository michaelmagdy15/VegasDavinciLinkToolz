import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

items = tl.GetItemListInTrack('video', 23)
for it in items:
    if '8192' in it.GetName():
        print(f"Fixing {it.GetName()}...")
        it.SetProperty('Pan', 0.0)
        it.SetProperty('Tilt', 0.0)
        it.SetProperty('ZoomX', 1.0)
        it.SetProperty('ZoomY', 1.0)
        it.SetProperty('ZoomGang', True)
        it.SetProperty('Scaling', 3)
        print("Readback:")
        print("  Pan:", it.GetProperty('Pan'))
        print("  Tilt:", it.GetProperty('Tilt'))
        print("  ZoomX:", it.GetProperty('ZoomX'))
        print("  Scaling:", it.GetProperty('Scaling'))
        break
