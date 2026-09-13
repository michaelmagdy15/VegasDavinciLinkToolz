import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"c:\Users\Mi5a\VegasDavinciLinkTool")
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
print(f"Timeline: {tl.GetName()}")

for t in range(1, tl.GetTrackCount("audio") + 1):
    items = tl.GetItemListInTrack("audio", t)
    if items:
        item = items[0]
        print(f"A{t} Item: '{item.GetName()}'")
        try:
            props = item.GetProperty()
            print(f"   Props: {props}")
        except Exception as e:
            print(f"   GetProperty() error: {e}")
        break
