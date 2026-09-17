import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print("=== 1. FIXING ALL CLIPS WITH BAD PAN / TILT / ZOOM ===")
fixed_count = 0
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        px = it.GetProperty('Pan')
        py = it.GetProperty('Tilt')
        zx = it.GetProperty('ZoomX')
        zy = it.GetProperty('ZoomY')
        
        # Detect clips with the -746.67 artifact or zoom 0.5625
        needs_fix = False
        if abs(px - (-746.67)) < 5.0 or abs(py - (-746.67)) < 5.0:
            needs_fix = True
        elif abs(px) > 10.0 or abs(py) > 10.0:
            needs_fix = True
        elif abs(zx - 0.5625) < 0.05 or abs(zx - 0.8083) < 0.05 or abs(zx - 0.585) < 0.05:
            needs_fix = True
            
        if needs_fix:
            print(f"Fixing V{t_idx} '{it.GetName()}': Pan=({px}, {py}) -> (0,0), Zoom=({zx}, {zy}) -> (1,1)")
            it.SetProperty('Pan', 0.0)
            it.SetProperty('Tilt', 0.0)
            it.SetProperty('ZoomX', 1.0)
            it.SetProperty('ZoomY', 1.0)
            it.SetProperty('ZoomGang', True)
            it.SetProperty('Scaling', 3)
            fixed_count += 1

print(f"Fixed {fixed_count} transform-broken clips!")

print("\n=== 2. FIXING CLIPS THAT ARE BLACK (GAIN = 0.0) ===")
black_fixed = 0
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        if it.GetFusionCompCount() > 0:
            comp = it.GetFusionCompByIndex(1)
            tools = comp.GetToolList()
            bc = next((t for t in tools.values() if t.ID == 'BrightnessContrast'), None)
            mi = next((t for t in tools.values() if t.ID == 'MediaIn'), None)
            mo = next((t for t in tools.values() if t.ID == 'MediaOut'), None)
            
            if bc:
                # If Gain at frame 0 is 0.0, it was an improperly keyframed fade
                g0 = bc.GetInput('Gain', 0)
                dur = it.GetDuration()
                # Check if it has keyframes
                if g0 == 0.0:
                    print(f"Fixing black clip V{t_idx} '{it.GetName()}' (dur={dur}):")
                    # If clip is very short (<= 8 frames), delete BC so it's not black
                    if dur <= 10:
                        comp.SetActiveTool(bc)
                        bc.Delete()
                        if mi and mo:
                            mo.ConnectInput("Input", mi)
                        print("  Short clip: Removed BrightnessContrast, connected MediaIn -> MediaOut")
                    else:
                        # Ensure gain[0] is 1.0
                        bc.Gain[0] = 1.0
                        print("  Set Gain[0] = 1.0 to ensure clip is visible from the start!")
                    black_fixed += 1

print(f"Fixed {black_fixed} black clips!")

print("\n=== 3. MUTING UNUSED SCRATCH TRACK V4 ('pick 5') ===")
# VEGAS Track 34 ('pick 5') was muted
tl.SetTrackEnable('video', 4, False)
print("Track V4 ('pick 5') disabled!")
