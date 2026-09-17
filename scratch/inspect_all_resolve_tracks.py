import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print(f"{'Resolve Track':<15} | {'Clips':<6} | Name")
print("-" * 50)
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    t_name = tl.GetTrackName('video', t_idx)
    items = tl.GetItemListInTrack('video', t_idx) or []
    print(f"Track V{t_idx:<8} | {len(items):<6} | {t_name}")
