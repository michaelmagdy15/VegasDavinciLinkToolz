import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print(f"Timeline Name: {tl.GetName()}")
print(f"Start Frame: {tl.GetStartFrame()}")
print(f"Track Count (Video): {tl.GetTrackCount('video')}")
print(f"Track Count (Audio): {tl.GetTrackCount('audio')}")

print("\n=== VIDEO TRACKS & CLIPS IN RESOLVE ===")
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    track_name = tl.GetTrackName('video', t_idx)
    print(f"\n--- Track V{t_idx}: '{track_name}' ({len(items)} items) ---")
    for item in items[:15]: # Show first 15 items per track
        name = item.GetName()
        start = item.GetStart()
        end = item.GetEnd()
        dur = item.GetDuration()
        mp = item.GetMediaPoolItem()
        clip_p = mp.GetClipProperty() if mp else {}
        file_p = clip_p.get('File Path', 'No File')
        print(f"  [{start} -> {end}] (dur {dur}) | Name: '{name}' | File: {file_p}")
