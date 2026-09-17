import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

for track_num in [24, 27]:
    items = tl.GetItemListInTrack('video', track_num) or []
    print(f"\n--- Track V{track_num} ({tl.GetTrackName('video', track_num)}) ---")
    for item in items[:5]:
        props = {}
        for p in ['CompositeMode', 'Opacity', 'ZoomX', 'ZoomY']:
            try: props[p] = item.GetProperty(p)
            except Exception as e: props[p] = str(e)
        print(f"  Item '{item.GetName()}': {props}")
