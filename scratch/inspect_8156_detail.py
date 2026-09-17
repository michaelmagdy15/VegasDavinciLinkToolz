import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

items = tl.GetItemListInTrack('video', 12)
item_8156 = None
for item in items:
    if '8156' in item.GetName():
        item_8156 = item
        break

if item_8156:
    print(f"Found 8156 on V12: {item_8156.GetName()}")
    print(f"Start: {item_8156.GetStart()}, End: {item_8156.GetEnd()}, Dur: {item_8156.GetDuration()}")
    print(f"LeftOffset: {item_8156.GetLeftOffset()}, RightOffset: {item_8156.GetRightOffset()}")
    
    # Check all properties
    for prop in ['Opacity', 'CompositeMode', 'Pan', 'Tilt', 'ZoomX', 'ZoomY', 'RotationAngle', 'CropLeft', 'CropRight', 'CropTop', 'CropBottom']:
        try:
            val = item_8156.GetProperty(prop)
            print(f"  Property {prop}: {val}")
        except Exception as e:
            print(f"  Property {prop}: error {e}")
            
    # Check fusion comp count
    fc_count = item_8156.GetFusionCompCount()
    print(f"FusionCompCount: {fc_count}")
    if fc_count > 0:
        comp = item_8156.GetFusionCompByIndex(1)
        tools = comp.GetToolList()
        print(f"Fusion tools: {[t.Name for t in tools.values()]}")
        for t in tools.values():
            print(f"  Tool {t.Name} ({t.ID})")

    # Check track enable for track 12
    # Check item enabled
    # In Resolve API: item.GetProperty('IsEnabled') or item.GetClipEnabled()?
    try:
        print(f"ClipEnabled: {item_8156.GetClipEnabled()}")
    except Exception as e:
        print(f"GetClipEnabled err: {e}")
else:
    print("8156 NOT found on V12!")
