import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
print(f"Current project timelineFrameRate: {proj.GetSetting('timelineFrameRate')}")

# Test setting timelineFrameRate
ok = proj.SetSetting("timelineFrameRate", "29.97")
print(f"SetSetting('timelineFrameRate', '29.97') result: {ok}")
print(f"New project timelineFrameRate: {proj.GetSetting('timelineFrameRate')}")
