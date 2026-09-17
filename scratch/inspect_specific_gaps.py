import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app, load_manifest_json
from pathlib import Path

resolve = get_resolve_app()
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
fps = float(tl.GetSetting('timelineFrameRate') or 29.97)
start_f = tl.GetStartFrame()

print(f"Active timeline: {tl.GetName()} (StartFrame={start_f}, FPS={fps})")

for target_f in [108325, 108395]:
    target_ms = (target_f - start_f) * 1000.0 / fps
    print(f"\n--- Checking around frame {target_f} ({target_ms:.1f}ms / {target_ms/1000:.2f}s) ---")
    for t_idx in range(tl.GetTrackCount('video'), 0, -1):
        items = tl.GetItemListInTrack('video', t_idx) or []
        for it in items:
            s = it.GetStart()
            e = it.GetEnd()
            if (s - 10) <= target_f <= (e + 10):
                print(f"  V{t_idx:2d} ({tl.GetTrackName('video', t_idx):15s}): '{it.GetName()}' [{s} -> {e}]")
