import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
print("Current Project:", p.GetName())

current_tl = p.GetCurrentTimeline()
print("Current Timeline:", current_tl.GetName())
print("Current Page:", r.GetCurrentPage())
