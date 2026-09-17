import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

cur_tc = tl.GetCurrentTimecode()
print(f"Current Timecode: {cur_tc}")

# Convert timecode to frame
# 01:00:00:00 = 86400 (at 24fps)
# Let's compute frame from timecode
parts = [int(x) for x in cur_tc.split(':')]
frame = (parts[0] * 3600 + parts[1] * 60 + parts[2]) * 24 + parts[3]
print(f"Current frame: {frame}")

print(f"\n--- Checking all tracks at frame {frame} ---")
found_any = False
for t_idx in range(tl.GetTrackCount('video'), 0, -1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        if it.GetStart() <= frame < it.GetEnd():
            found_any = True
            print(f"\nTrack V{t_idx} ({tl.GetTrackName('video', t_idx)}): Clip '{it.GetName()}' [Start={it.GetStart()}, End={it.GetEnd()}]")
            for p in ['Pan', 'Tilt', 'ZoomX', 'ZoomY', 'RotationAngle', 'AnchorPointX', 'AnchorPointY', 'CompositeMode', 'Opacity', 'Scaling']:
                try:
                    val = it.GetProperty(p)
                    print(f"    {p}: {val}")
                except Exception as e:
                    pass
            mp = it.GetMediaPoolItem()
            if mp:
                cp = mp.GetClipProperty()
                print(f"    MediaPool: Resolution={cp.get('Resolution')}, FPS={cp.get('FPS')}, Clip Name={cp.get('Clip Name')}")
            if it.GetFusionCompCount() > 0:
                print(f"    Fusion Comp Count: {it.GetFusionCompCount()}")
                comp = it.GetFusionCompByIndex(1)
                for tid, tool in comp.GetToolList().items():
                    print(f"      Tool: {tool.GetAttrs().get('TOOLS_Name')} ({tool.GetAttrs().get('TOOLS_RegID')})")

if not found_any:
    print("NO CLIPS FOUND AT THIS FRAME! (Gap!)")
