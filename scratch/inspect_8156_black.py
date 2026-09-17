import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

items_v12 = tl.GetItemListInTrack('video', 12) or []
for it in items_v12:
    if '8156' in it.GetName():
        print(f"Item: {it.GetName()}")
        print(f"CompositeMode: {it.GetProperty('CompositeMode')}")
        print(f"Opacity: {it.GetProperty('Opacity')}")
        print(f"FusionCompCount: {it.GetFusionCompCount()}")
        
        # Let's inspect the comp
        if it.GetFusionCompCount() > 0:
            comp = it.GetFusionCompByIndex(1)
            print("Tools:")
            for tid, t in comp.GetToolList().items():
                print(f"  {t.Name} ({t.ID})")
                if t.ID == 'BrightnessContrast':
                    # Check gain values at each frame 0 to 5
                    for f in range(6):
                        try:
                            # In Fusion: t.Gain[f] or t.GetInput('Gain', f)
                            print(f"    Gain at frame {f}: {t.GetInput('Gain', f)}")
                        except Exception as e:
                            print(f"    Gain at frame {f} err: {e}")
                elif t.ID == 'MediaIn':
                    for inp in ['HoldFirstFrame', 'HoldLastFrame', 'SourceTrack', 'GlobalIn', 'GlobalOut']:
                        try:
                            print(f"    {inp}: {t.GetInput(inp)}")
                        except Exception as e:
                            pass
        break
