import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print(f"Timeline: {tl.GetName()}")
print(f"Total video tracks: {tl.GetTrackCount('video')}")

messed_up_clips = []
all_clips = []

for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        px = it.GetProperty('Pan')
        py = it.GetProperty('Tilt')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        rot = it.GetProperty('RotationAngle')
        all_clips.append((t_idx, it, px, py, zx, zy, rot))
        
        # Check if Pan or Tilt is around -746 or non-zero, or Zoom is 0.5625
        is_bad = False
        if abs(px) > 10.0 or abs(py) > 10.0:
            is_bad = True
        if abs(zx - 1.0) > 0.01 or abs(zy - 1.0) > 0.01:
            is_bad = True
            
        if is_bad:
            messed_up_clips.append((t_idx, it.GetName(), it.GetStart(), it.GetEnd(), px, py, zx, zy, rot))

print(f"Total clips inspected: {len(all_clips)}")
print(f"Messed up clips count: {len(messed_up_clips)}")

print("\n--- Messed up clips list ---")
for t_idx, name, s, e, px, py, zx, zy, rot in messed_up_clips:
    print(f"V{t_idx:2d} | [{s:5d} -> {e:5d}] | {name:<35s} | Pan=({px:7.1f}, {py:7.1f}) | Zoom=({zx:.3f}, {zy:.3f}) | Rot={rot}")
