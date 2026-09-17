import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

print("Auditing all clips with Fusion comps:")
for t_idx in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t_idx) or []
    for it in items:
        if it.GetFusionCompCount() > 0:
            for cidx in range(1, it.GetFusionCompCount() + 1):
                comp = it.GetFusionCompByIndex(cidx)
                for tid, t in comp.GetToolList().items():
                    if t.ID == 'BrightnessContrast':
                        gain = t.GetInput('Gain')
                        # Check at frame 0
                        gain0 = t.GetInput('Gain', 0)
                        print(f"V{t_idx} '{it.GetName()}': BrightnessContrast Gain default={gain}, frame 0={gain0}")
