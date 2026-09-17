import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
print(f"Project: {proj.GetName()}")

tl_count = proj.GetTimelineCount()
print(f"Found {tl_count} timelines.")

total_fixed = 0

for i in range(1, tl_count + 1):
    tl = proj.GetTimelineByIndex(i)
    tl_name = tl.GetName()
    print(f"\n==========================================")
    print(f"Checking Timeline {i}: '{tl_name}'")
    print(f"==========================================")
    
    num_v = tl.GetTrackCount('video')
    tl_fixed = 0
    
    for t_idx in range(1, num_v + 1):
        track_name = tl.GetTrackName('video', t_idx)
        items = tl.GetItemListInTrack('video', t_idx) or []
        for it in items:
            comp_count = it.GetFusionCompCount()
            if comp_count == 0:
                continue
            
            for c_idx in range(1, comp_count + 1):
                comp = it.GetFusionCompByIndex(c_idx)
                if not comp:
                    continue
                
                tools = comp.GetToolList()
                bc_tools = []
                media_in = None
                media_out = None
                other_tools = []
                
                for k, tool in tools.items():
                    tname = tool.Name
                    if 'BrightnessContrast' in tname:
                        bc_tools.append(tool)
                    elif 'MediaIn' in tname:
                        media_in = tool
                    elif 'MediaOut' in tname:
                        media_out = tool
                    else:
                        other_tools.append(tool)
                
                if bc_tools:
                    print(f"  [FOUND] V{t_idx} ('{track_name}') -> Clip: '{it.GetName()}' has {len(bc_tools)} BrightnessContrast tool(s)")
                    if media_in and media_out:
                        # If there are no other custom effect tools, connect MediaIn directly to MediaOut
                        if not other_tools:
                            media_out.ConnectInput("Input", media_in)
                        for bc in bc_tools:
                            print(f"    -> Deleting tool: {bc.Name}")
                            bc.Delete()
                        tl_fixed += 1
                        total_fixed += 1
                    else:
                        # Just delete the BrightnessContrast tool
                        for bc in bc_tools:
                            print(f"    -> Deleting tool: {bc.Name}")
                            bc.Delete()
                        tl_fixed += 1
                        total_fixed += 1

    print(f"Timeline '{tl_name}': removed BrightnessContrast from {tl_fixed} clips.")

print(f"\n[DONE] Total clips fixed across all timelines: {total_fixed}")
