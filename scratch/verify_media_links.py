import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
print(f"Checking media status on timeline '{tl.GetName()}':")

offline_clips = []
online_clips = 0

for t in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        mp = it.GetMediaPoolItem()
        name = it.GetName()
        if not mp:
            offline_clips.append((f"V{t}", name, "No MediaPoolItem"))
            continue
        props = mp.GetClipProperty() or {}
        fp = props.get('File Path', '')
        if not fp:
            # Generator or solid color or compound?
            offline_clips.append((f"V{t}", name, "Empty File Path"))
        elif not os.path.exists(fp):
            offline_clips.append((f"V{t}", name, f"File does not exist on disk: {fp}"))
        else:
            online_clips += 1

print(f"Online clips: {online_clips}")
print(f"Offline / unlinked clips: {len(offline_clips)}")
for tr, name, reason in offline_clips:
    print(f"  [{tr}] {name}: {reason}")
