import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

start_frame = tl.GetStartFrame()
print(f"Timeline Start Frame: {start_frame}")

print(f"\n{'Track':<10} | {'Name':<20} | {'Start':<8} | {'End':<8} | {'Dur':<6} | Clip Name")
print("-" * 80)

# Check all clips that overlap the first 5 seconds (start_frame to start_frame + 150)
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    t_name = tl.GetTrackName('video', t_idx)
    items = tl.GetItemListInTrack('video', t_idx) or []
    for item in items:
        s = item.GetStart()
        e = item.GetEnd()
        if s <= start_frame + 250 and e >= start_frame:
            cname = item.GetName()
            print(f"V{t_idx:<9} | {t_name:<20} | {s:<8} | {e:<8} | {e-s:<6} | {cname}")
