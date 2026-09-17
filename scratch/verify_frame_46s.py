import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

tl.SetCurrentTimecode("01:00:46:00")
print(f"Playhead set to 01:00:46:00")

# Check all clips active at 87504
print("\nActive clips at 01:00:46:00:")
for t_idx in range(tl.GetTrackCount('video'), 0, -1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        if it.GetStart() <= 87504 < it.GetEnd():
            print(f"V{t_idx:2d} ({tl.GetTrackName('video', t_idx):15s}) | {it.GetName()} | CompMode={it.GetProperty('CompositeMode')} Opacity={it.GetProperty('Opacity')} Pan=({it.GetProperty('Pan')}, {it.GetProperty('Tilt')}) Zoom=({it.GetProperty('ZoomX')}, {it.GetProperty('ZoomY')})")
