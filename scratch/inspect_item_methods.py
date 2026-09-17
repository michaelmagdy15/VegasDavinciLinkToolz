import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
item = tl.GetItemListInTrack('video', 12)[0]

print("=== TIMELINE ITEM METHODS ===")
methods = [m for m in dir(item) if not m.startswith('__')]
for m in sorted(methods):
    print(f"  {m}")
