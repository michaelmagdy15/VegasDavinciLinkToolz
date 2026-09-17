import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

cur_tc = tl.GetCurrentTimecode()
print(f"Current Timecode: {cur_tc}")

# Let's inspect the timeline format/settings
print("\n--- Timeline Settings ---")
for s in ['timelineResolutionWidth', 'timelineResolutionHeight', 'timelineFrameRate', 'timelineCropImageStyle', 'timelineInputRescaling']:
    print(f"  {s}: {tl.GetSetting(s)}")

# Inspect all clips on all video tracks at the current timecode or start frame
start_f = tl.GetStartFrame()
print(f"\n--- Checking all tracks at start frame {start_f} ---")

for t_idx in range(tl.GetTrackCount('video'), 0, -1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        if it.GetStart() <= start_f < it.GetEnd():
            print(f"\nTrack V{t_idx} ({tl.GetTrackName('video', t_idx)}): {it.GetName()}")
            # Check all properties
            props = [
                'Pan', 'Tilt', 'ZoomX', 'ZoomY', 'RotationAngle', 'AnchorPointX', 'AnchorPointY',
                'Pitch', 'Yaw', 'CompositeMode', 'Opacity', 'CropLeft', 'CropRight', 'CropTop', 'CropBottom',
                'RetimeProcess', 'MotionEstimation', 'Scaling'
            ]
            for p in props:
                try:
                    val = it.GetProperty(p)
                    if val not in [0.0, 1.0, 0, None, '']:
                        print(f"    {p}: {val}")
                    elif p in ['Pan', 'Tilt', 'ZoomX', 'ZoomY', 'RotationAngle', 'Scaling']:
                        print(f"    {p}: {val}")
                except Exception as e:
                    pass
            # Check fusion comp
            if it.GetFusionCompCount() > 0:
                print(f"    Fusion comps: {it.GetFusionCompCount()}")
                comp = it.GetFusionCompByIndex(1)
                for tid, tool in comp.GetToolList().items():
                    print(f"      Fusion tool: {tool.GetAttrs().get('TOOLS_Name')} ({tool.GetAttrs().get('TOOLS_RegID')})")
