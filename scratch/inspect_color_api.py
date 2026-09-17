import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
it = tl.GetItemListInTrack('video', 12)[0]

print('=== TimelineItem Color Methods ===')
for m in dir(it):
    if any(k in m.lower() for k in ['color', 'lut', 'grade', 'node', 'drx', 'cdl', 'still']):
        print(' ', m)

print('=== Timeline Color Methods ===')
for m in dir(tl):
    if any(k in m.lower() for k in ['color', 'lut', 'grade', 'node', 'drx', 'cdl', 'still']):
        print(' ', m)

print('=== Project Color Settings ===')
for s in ['colorScienceMode', 'isColorManagementEnabled', 'timelineWorkingColorSpace', 'timelineWorkingColorSpaceGamma']:
    try:
        print(f'  {s}: {p.GetSetting(s)}')
    except Exception as e:
        print(f'  {s}: err {e}')
