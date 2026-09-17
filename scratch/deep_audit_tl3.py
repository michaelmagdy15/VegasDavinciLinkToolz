import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
print(f"Auditing Timeline: {tl.GetName()} ({tl.GetSetting('timelineFrameRate')} fps)")

drone_clips = []
camera_clips = []
other_clips = []

for t in range(1, tl.GetTrackCount('video') + 1):
    tname = tl.GetTrackName('video', t)
    for it in tl.GetItemListInTrack('video', t) or []:
        mp_it = it.GetMediaPoolItem()
        fp = mp_it.GetClipProperty('File Path') if mp_it else ''
        name = it.GetName()
        rot = it.GetProperty('RotationAngle')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        pan = it.GetProperty('Pan')
        tilt = it.GetProperty('Tilt')
        scaling = it.GetProperty('Scaling')
        comp_mode = it.GetProperty('CompositeMode')
        opacity = it.GetProperty('Opacity')
        
        info = {
            'track': f'V{t} ({tname})',
            'name': name,
            'file': fp,
            'rot': rot,
            'zx': zx,
            'zy': zy,
            'pan': pan,
            'tilt': tilt,
            'scaling': scaling,
            'comp_mode': comp_mode,
            'opacity': opacity
        }
        
        fn_l = name.lower()
        if 'dji' in fn_l or 'drone' in fn_l:
            drone_clips.append(info)
        elif 'a7' in fn_l or 'abdra' in fn_l:
            camera_clips.append(info)
        else:
            other_clips.append(info)

print(f"\nTotal Video Items: Drone={len(drone_clips)}, Camera={len(camera_clips)}, Other={len(other_clips)}")

print("\n--- SAMPLE DRONE CLIPS (should be rot 0) ---")
for c in drone_clips[:5]:
    print(f"  {c['track']} | {c['name']} -> Rot={c['rot']}, Zoom={c['zx']}, Pan={c['pan']}, Tilt={c['tilt']}, Scaling={c['scaling']}")

print("\n--- SAMPLE CAMERA CLIPS ---")
for c in camera_clips[:8]:
    print(f"  {c['track']} | {c['name']} -> Rot={c['rot']}, Zoom={c['zx']}, Pan={c['pan']}, Tilt={c['tilt']}, Scaling={c['scaling']}")

# Check for non-zero rotations in camera clips
rot_camera = [c for c in camera_clips if abs(c['rot']) > 0.01]
print(f"\nCamera clips with non-zero rotation: {len(rot_camera)} / {len(camera_clips)}")
for c in rot_camera[:10]:
    print(f"  {c['name']} -> Rot={c['rot']}")

# Check for non-zero rotations in drone clips
rot_drone = [c for c in drone_clips if abs(c['rot']) > 0.01]
print(f"\nDrone clips with non-zero rotation: {len(rot_drone)} / {len(drone_clips)}")

# Check for abnormal transforms across all clips
abnormal = [c for c in (drone_clips + camera_clips) if abs(c['pan']) > 500 or abs(c['tilt']) > 500 or abs(c['zx'] - 1.0) > 0.4]
print(f"\nClips with extreme/abnormal transforms (pan/tilt > 500 or zoom deviate > 0.4): {len(abnormal)}")
for c in abnormal:
    print(f"  {c['track']} | {c['name']} -> Rot={c['rot']}, Zoom={c['zx']}, Pan={c['pan']}, Tilt={c['tilt']}")
