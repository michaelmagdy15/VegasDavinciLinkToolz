import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetTimelineByIndex(3)
print("Timeline 3 Name:", tl.GetName(), "FPS:", tl.GetSetting("timelineFrameRate"))

# Check clip 8156
found_8156 = False
for t in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        if '8156' in it.GetName():
            found_8156 = True
            comp = it.GetFusionCompByIndex(1)
            print(f"Clip 8156 on V{t}: Fusion Comp exists: {comp is not None}")
            if comp:
                tools = comp.GetToolList()
                print(f"  Tools in 8156: {[tools[k].GetName() for k in tools]}")
            print(f"  Opacity: {it.GetProperty('Opacity')}")
            print(f"  CompositeMode: {it.GetProperty('CompositeMode')}")
            print(f"  Scaling: {it.GetProperty('Scaling')}")
            print(f"  Pan: {it.GetProperty('Pan')}, Tilt: {it.GetProperty('Tilt')}, ZoomX: {it.GetProperty('ZoomX')}")

# Check rotation of a couple camera clips
for t in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        name = it.GetName()
        if '8192' in name or '8227' in name or '0014_D' in name:
            print(f"Clip {name} on V{t}: Pan={it.GetProperty('Pan')}, Tilt={it.GetProperty('Tilt')}, ZoomX={it.GetProperty('ZoomX')}, Rotation={it.GetProperty('RotationAngle')}")
