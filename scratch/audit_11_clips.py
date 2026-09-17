import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app, load_manifest_json
from pathlib import Path

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

d = load_manifest_json(str(Path.home() / '.timeline_bridge' / 'vegas_timeline.json'))
v_clips = {}
for t in d.get('tracks', []):
    for c in t.get('clips', []):
        v_clips[c.get('name')] = c

print("Auditing the 11 clips:")
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        px = it.GetProperty('Pan')
        py = it.GetProperty('Tilt')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        rot = it.GetProperty('RotationAngle')
        
        if rot != 0.0 or abs(px) > 1.0 or abs(py) > 1.0 or abs(zx - 1.0) > 0.05:
            print(f"V{t_idx:2d} | [{it.GetStart()}->{it.GetEnd()}] | {it.GetName()}")
            print(f"   Current: Pan=({px}, {py}), Zoom=({zx}, {zy}), Rot={rot}")
            vc = v_clips.get(it.GetName())
            if vc:
                print(f"   Vegas:   pan=({vc.get('pan_x')}, {vc.get('pan_y')}), zoom=({vc.get('zoom_x')}), rot={vc.get('rotation_angle')}")
