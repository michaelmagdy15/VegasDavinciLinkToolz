import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

# Move playhead to 86400
tl.SetCurrentTimecode("01:00:00:00")
print("Playhead moved to 01:00:00:00")

# Check item on V12
items_v12 = tl.GetItemListInTrack('video', 12) or []
item_8156 = None
for it in items_v12:
    if '8156' in it.GetName():
        item_8156 = it
        break

if item_8156:
    print(f"Item 8156 found: {item_8156.GetName()}")
    print(f"Duration: {item_8156.GetDuration()} frames")
    print(f"Fusion comp count: {item_8156.GetFusionCompCount()}")
    if item_8156.GetFusionCompCount() > 0:
        comp = item_8156.GetFusionCompByIndex(1)
        print("Tools in Fusion comp:")
        for t in comp.GetToolList().values():
            print(f"  {t.Name} ({t.ID})")
            # Let's check error status on MediaIn1
            if t.ID == 'MediaIn':
                # Check if it has an error or valid clip
                try:
                    props = t.GetInput("MediaProps")
                    print(f"    MediaProps: {props}")
                except Exception as e:
                    print(f"    MediaProps err: {e}")
