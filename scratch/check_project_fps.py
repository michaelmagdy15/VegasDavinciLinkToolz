import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
for s in ['timelineFrameRate', 'timelinePlaybackFrameRate', 'videoFrameRate']:
    print(f"Project setting {s}: {proj.GetSetting(s)}")
