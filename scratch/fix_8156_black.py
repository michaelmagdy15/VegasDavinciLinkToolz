import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

items_v12 = tl.GetItemListInTrack('video', 12) or []
for it in items_v12:
    if '8156' in it.GetName():
        print("Fixing 8156...")
        # 1. Reset composite mode to 0 (Normal) or as intended
        it.SetProperty("CompositeMode", 0)
        it.SetProperty("Opacity", 100.0)
        
        # 2. Fix the Fusion Comp
        if it.GetFusionCompCount() > 0:
            comp = it.GetFusionCompByIndex(1)
            # Find BrightnessContrast and delete it, connect MediaIn directly to MediaOut
            tools = comp.GetToolList()
            mi = None
            mo = None
            bc = None
            for t in tools.values():
                if t.ID == 'MediaIn': mi = t
                elif t.ID == 'MediaOut': mo = t
                elif t.ID == 'BrightnessContrast': bc = t
            
            if bc:
                comp.SetActiveTool(bc)
                bc.Delete()
                print("Deleted BrightnessContrast tool!")
            if mi and mo:
                mo.ConnectInput("Input", mi)
                print("Connected MediaIn1 directly to MediaOut1!")
        
        print("8156 fixed successfully!")
        break
