import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetTimelineByIndex(3)

print(f"Auditing transforms on {tl.GetName()}:")
bad_transforms = []
for t in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        pan = it.GetProperty('Pan')
        tilt = it.GetProperty('Tilt')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        sc = it.GetProperty('Scaling')
        if abs(pan) > 100 or abs(tilt) > 100 or abs(zx - 1.0) > 0.4:
            bad_transforms.append((t, it.GetName(), pan, tilt, zx, zy, sc))

print(f"Clips with suspicious transforms: {len(bad_transforms)}")
for t, name, pan, tilt, zx, zy, sc in bad_transforms:
    print(f"  V{t}: {name} -> Pan={pan}, Tilt={tilt}, ZoomX={zx}, Scaling={sc}")
