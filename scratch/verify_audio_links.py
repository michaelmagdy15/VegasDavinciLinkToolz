import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
print(f"Checking audio media status on timeline '{tl.GetName()}':")

offline_audio = []
online_audio = 0

for a in range(1, tl.GetTrackCount('audio') + 1):
    items = tl.GetItemListInTrack('audio', a) or []
    for it in items:
        mp = it.GetMediaPoolItem()
        name = it.GetName()
        if not mp:
            offline_audio.append((f"A{a}", name, "No MediaPoolItem"))
            continue
        props = mp.GetClipProperty() or {}
        fp = props.get('File Path', '')
        if not fp:
            offline_audio.append((f"A{a}", name, "Empty File Path"))
        elif not os.path.exists(fp):
            offline_audio.append((f"A{a}", name, f"File does not exist: {fp}"))
        else:
            online_audio += 1

print(f"Online audio clips: {online_audio}")
print(f"Offline audio clips: {len(offline_audio)}")
for tr, name, reason in offline_audio:
    print(f"  [{tr}] {name}: {reason}")
