import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

start_f = 86400
end_f = 86450

print(f"=== CLIPS OVERLAPPING FRAMES {start_f} -> {end_f} (HIGHEST TO LOWEST TRACK) ===")
# Resolve evaluates tracks from top to bottom (V31 down to V1)
for t_idx in range(tl.GetTrackCount('video'), 0, -1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for item in items:
        s = item.GetStart()
        e = item.GetEnd()
        if s < end_f and e > start_f:
            t_name = tl.GetTrackName('video', t_idx)
            mp = item.GetMediaPoolItem()
            clip_p = mp.GetClipProperty() if mp else {}
            fn = clip_p.get('File Name', item.GetName())
            comp = item.GetProperty('CompositeMode')
            op = item.GetProperty('Opacity')
            print(f"V{t_idx:2d} ({t_name:15s}) | Frames [{s:5d} -> {e:5d}] (dur {e-s:2d}) | CompMode={comp} Opacity={op} | {fn}")
