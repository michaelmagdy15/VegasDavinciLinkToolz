import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()

# Test on a Sony clip on V12 (8156)
it_sony = None
for it in tl.GetItemListInTrack('video', 12):
    if '8156' in it.GetName():
        it_sony = it
        break

if it_sony:
    print("Found Sony clip:", it_sony.GetName())
    print("Current LUT:", it_sony.GetLUT(1))
    res = it_sony.SetLUT(1, r"VEGAS_Imported\Arrow_Vibrant_Turquoise_Sony_A7.cube")
    print("SetLUT res:", res)
    print("New LUT:", it_sony.GetLUT(1))

# Test on a DJI clip on V11
it_dji = None
for it in tl.GetItemListInTrack('video', 11):
    if 'DJI' in it.GetName():
        it_dji = it
        break

if it_dji:
    print("\nFound DJI clip:", it_dji.GetName())
    print("Current LUT:", it_dji.GetLUT(1))
    res = it_dji.SetLUT(1, r"VEGAS_Imported\Arrow_Vibrant_Turquoise_DJI_Drone.cube")
    print("SetLUT res:", res)
    print("New LUT:", it_dji.GetLUT(1))
