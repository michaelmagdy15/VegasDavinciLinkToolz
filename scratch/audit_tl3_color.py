import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
tl = r.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
print(f"Auditing Color Page nodes on '{tl.GetName()}':")

lut_clips = 0
no_lut_clips = 0

for t in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        name = it.GetName()
        # In Resolve API:
        # it.GetNodeLUT(nodeIndex) or it.GetLUT() or it.GetColorNodeCount()
        try:
            lut = it.GetLUT(1)
        except Exception:
            lut = None
        
        # Check node count if available
        # Resolve API: item.GetLUT(nodeIndex)
        node_lut = None
        for n in range(1, 5):
            try:
                nl = it.GetLUT(n)
                if nl:
                    node_lut = nl
                    break
            except Exception:
                pass
        
        if node_lut or lut:
            lut_clips += 1
            print(f"  [LUT] V{t} {name} -> Node LUT: {node_lut or lut}")
        else:
            no_lut_clips += 1

print(f"Total checked: with LUT={lut_clips}, without direct item LUT={no_lut_clips}")
