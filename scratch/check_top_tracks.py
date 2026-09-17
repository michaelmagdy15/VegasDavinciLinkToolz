import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

for t in [28, 30]:
    items = tl.GetItemListInTrack('video', t) or []
    tn = tl.GetTrackName('video', t)
    print(f"Track V{t} ({tn}):")
    for it in items:
        cm = it.GetProperty("CompositeMode")
        op = it.GetProperty("Opacity")
        print(f"  [{it.GetStart()} -> {it.GetEnd()}] {it.GetName()} comp={cm} op={op}")
