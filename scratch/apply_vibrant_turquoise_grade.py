import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()

print(f"Applying 'Vibrant Turquoise Lagoon & Golden Sun Pop' Grade to: '{tl.GetName()}'")

# Ensure Resolve has registered the latest LUTs
p.RefreshLUTList()

sony_lut = "VEGAS_Imported/Arrow_Vibrant_Turquoise_Sony_A7.cube"
dji_lut = "VEGAS_Imported/Arrow_Vibrant_Turquoise_DJI_Drone.cube"

sony_count = 0
dji_count = 0
skipped_count = 0

for t in range(1, tl.GetTrackCount('video') + 1):
    tname = tl.GetTrackName('video', t)
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        name = it.GetName()
        name_l = name.lower()
        
        # Check if overlay
        if any(x in name_l for x in ['filmburn', 'film_burn', 'light_', 'white.png', 'adjustment']):
            skipped_count += 1
            continue
            
        if 'dji' in name_l or 'drone' in name_l:
            ok = it.SetLUT(1, dji_lut)
            if ok:
                dji_count += 1
            else:
                print(f"  [WARN] Failed to set DJI LUT on: V{t} {name}")
        elif any(x in name_l for x in ['a7iv', 'a7s', 'abdrafilms', '81', '82', '91', '92', '93', '00']):
            ok = it.SetLUT(1, sony_lut)
            if ok:
                sony_count += 1
            else:
                print(f"  [WARN] Failed to set Sony LUT on: V{t} {name}")
        else:
            # General camera / b-roll fallback: apply Sony LUT for natural skin & turquoise
            ok = it.SetLUT(1, sony_lut)
            if ok:
                sony_count += 1
            else:
                skipped_count += 1

print(f"\n[GRADE COMPLETE]")
print(f"  • Sony A7 camera clips graded: {sony_count}")
print(f"  • DJI Drone clips graded:      {dji_count}")
print(f"  • Overlays preserved clean:    {skipped_count}")
print(f"  • Total clips in timeline:     {sony_count + dji_count + skipped_count}")
