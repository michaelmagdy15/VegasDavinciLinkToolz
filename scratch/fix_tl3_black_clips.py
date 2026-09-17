import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetTimelineByIndex(3)

print("Fixing all pitch-black clips on Timeline 3:")
fixed = 0
for t in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        comp = it.GetFusionCompByIndex(1)
        if not comp:
            continue
        tools = comp.GetToolList()
        bc = None
        media_in = None
        media_out = None
        for k, tool in tools.items():
            tname = tool.Name
            if 'BrightnessContrast' in tname:
                bc = tool
            elif 'MediaIn' in tname:
                media_in = tool
            elif 'MediaOut' in tname:
                media_out = tool
        
        if bc and media_in and media_out:
            print(f"  Bypassing BrightnessContrast on V{t} clip: {it.GetName()}")
            media_out.ConnectInput("Input", media_in)
            bc.Delete()
            fixed += 1

print(f"Fixed {fixed} clips on Timeline 3.")
