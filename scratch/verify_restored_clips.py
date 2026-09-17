import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app
r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
check_names = ['8123', '8233', '8121', '9390', '9318', 'filmburn_6', '8120', '8118', 'White']
for t in range(1, tl.GetTrackCount('video') + 1):
    for it in tl.GetItemListInTrack('video', t) or []:
        for cn in check_names:
            if cn in it.GetName():
                comp = it.GetFusionCompByIndex(1)
                tools = [tool.Name for tool in comp.GetToolList().values()] if comp else []
                print(f"V{t} {it.GetName()}: Opacity={it.GetProperty('Opacity')}, CompMode={it.GetProperty('CompositeMode')}, Fusion={tools}")
