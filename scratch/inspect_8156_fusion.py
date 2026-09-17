import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

items = tl.GetItemListInTrack('video', 12)
for item in items:
    if '8156' in item.GetName():
        comp = item.GetFusionCompByIndex(1)
        tools = comp.GetToolList()
        for name, t in tools.items():
            print(f"Tool {name} ({t.ID}):")
            inputs = t.GetInputList()
            for inp_id, inp in inputs.items():
                val = t.GetInput(inp_id)
                # print non-default or interesting inputs
                if inp_id in ['Gain', 'Alpha', 'Clip', 'Blend', 'ProcessAlpha', 'ApplyMaskInverted']:
                    print(f"   {inp_id} = {val}")
        break
