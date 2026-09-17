import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app
r = get_resolve_app()
tl = r.GetProjectManager().GetCurrentProject().GetTimelineByIndex(3)
it = tl.GetItemListInTrack('video', 12)[0]
comp = it.GetFusionCompByIndex(1)

res = comp.Execute('BrightnessContrast1Gain:SetKeyFrames({[0] = {Value = 1.0}, [2] = {Value = 1.0}, [3] = {Value = 0.0}})')
print('Execute res:', res)

bc = None
for t in comp.GetToolList().values():
    if 'Brightness' in t.Name and not 'Gain' in t.Name: bc = t

for f in range(it.GetDuration()):
    print(f'Frame {f}: Gain = {bc.Gain[f]}')
