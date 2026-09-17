import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app, load_manifest_json
from pathlib import Path

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

d = load_manifest_json(str(Path.home() / '.timeline_bridge' / 'vegas_timeline.json'))

# Map VEGAS clips by name or approximate start
vegas_clips = {}
for t in d.get('tracks', []):
    for c in t.get('clips', []):
        vegas_clips[c.get('name')] = c

# Check the 12 items in Resolve
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        px = it.GetProperty('Pan')
        py = it.GetProperty('Tilt')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        rot = it.GetProperty('RotationAngle')
        
        is_bad = False
        if abs(px) > 10.0 or abs(py) > 10.0 or abs(zx - 1.0) > 0.01 or abs(zy - 1.0) > 0.01:
            is_bad = True
            
        if is_bad:
            cname = it.GetName()
            vc = None
            for vname, cand in vegas_clips.items():
                if vname in cname or Path(cand.get('media_path', '')).name in cname:
                    vc = cand
                    break
            print(f"==================================================")
            print(f"Resolve V{t_idx} [{it.GetStart()}->{it.GetEnd()}]: {cname}")
            print(f"  Resolve: Pan=({px}, {py}), Zoom=({zx}, {zy}), Rot={rot}")
            if vc:
                print(f"  VEGAS:   pan=({vc.get('pan_x')}, {vc.get('pan_y')}), zoom=({vc.get('zoom_x')}, {vc.get('zoom_y')}), rot={vc.get('rotation_angle')}")
                kfs = vc.get('motion_keyframes', [])
                print(f"  VEGAS Keyframes count: {len(kfs)}")
                for k in kfs[:3]:
                    print(f"    kf: pos={k.get('position_ms')}, zoom={k.get('zoom')}, pan=({k.get('pan_x')}, {k.get('pan_y')})")
