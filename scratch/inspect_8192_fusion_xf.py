import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

items = tl.GetItemListInTrack('video', 23)
for it in items:
    if '8192' in it.GetName():
        if it.GetFusionCompCount() > 0:
            comp = it.GetFusionCompByIndex(1)
            for tid, tool in comp.GetToolList().items():
                if 'Transform' in tool.GetAttrs().get('TOOLS_Name', ''):
                    print("Found Transform tool in Fusion:")
                    for in_id in ['Center', 'Size', 'Angle', 'Aspect']:
                        print(f"  {in_id}: {tool.GetInput(in_id)}")
                    # Check if it has keyframes
                    # If empty default: Center=(0.5, 0.5), Size=1.0, Angle=0.0
        break
