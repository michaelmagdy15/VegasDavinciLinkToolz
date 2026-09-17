import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app, load_manifest_json

r = get_resolve_app()
tl = r.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
markers = tl.GetMarkers() or {}
fps = float(tl.GetSetting('timelineFrameRate'))
start = tl.GetStartFrame()

print(f"Markers on '{tl.GetName()}': {len(markers)}")
for f, m in sorted(markers.items()):
    tc = (f - start) / fps
    print(f"  [{tc:05.2f}s] Marker '{m.get('name')}' (Color: {m.get('color')})")

m_json = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')
v_markers = m_json.get('markers', [])
print(f"\nMarkers in VEGAS manifest: {len(v_markers)}")
for vm in v_markers:
    pos_s = vm.get('position_ms', 0) / 1000.0
    print(f"  [{pos_s:05.2f}s] VEGAS Marker '{vm.get('name')}'")
