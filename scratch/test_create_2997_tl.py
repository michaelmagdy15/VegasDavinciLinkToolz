import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()

test_tl = mp.CreateEmptyTimeline("Test2997Timeline")
if test_tl:
    print(f"Created test timeline: {test_tl.GetName()}")
    print(f"Test timeline frame rate: {test_tl.GetSetting('timelineFrameRate')}")
    # Clean up test timeline
    # proj.SetCurrentTimeline(...)
