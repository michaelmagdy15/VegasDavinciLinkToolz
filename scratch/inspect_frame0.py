import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print(f"Current timeline: {tl.GetName()}")
print(f"Current timecode: {tl.GetCurrentTimecode()}")
print(f"Start frame: {tl.GetStartFrame()}")

# Check all clips at frame 86400
cur_f = 86400
print(f"\n--- Checking all tracks at frame {cur_f} ---")
for t_idx in range(tl.GetTrackCount('video'), 0, -1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    t_name = tl.GetTrackName('video', t_idx)
    # Check track enable
    # Note: Resolve API GetTrackEnable?
    for item in items:
        s = item.GetStart()
        e = item.GetEnd()
        if s <= cur_f < e:
            mp = item.GetMediaPoolItem()
            fn = item.GetName()
            comp = item.GetProperty('CompositeMode')
            op = item.GetProperty('Opacity')
            print(f"Track V{t_idx:2d} ({t_name:15s}): Clip '{fn}' [Start={s}, End={e}, Dur={e-s}] CompMode={comp}, Opacity={op}")
