import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

# Track V12 in Resolve
items = tl.GetItemListInTrack('video', 12) or []
for item in items:
    if '8156' in item.GetName():
        print("Found 8156 on Track V12:")
        print("  Start:", item.GetStart())
        print("  End:", item.GetEnd())
        print("  Duration:", item.GetDuration())
        props = ['CompositeMode', 'Opacity', 'Pan', 'Tilt', 'ZoomX', 'ZoomY', 'CropLeft', 'CropRight', 'CropTop', 'CropBottom', 'RotationAngle']
        for p in props:
            try: print(f"  {p}: {item.GetProperty(p)}")
            except Exception as e: print(f"  {p}: {e}")
        
        # Check fusion / color / markers
        print("  Node count (Color):", item.GetColorNodeCount())
        print("  CDL:", item.GetCDL())
        print("  LUT:", item.GetLUT(1) if hasattr(item, 'GetLUT') else 'N/A')
