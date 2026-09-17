import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

print("=== VEGAS PRO CLIPS FROM 0s TO 5s (TOP TRACK TO BOTTOM TRACK) ===")
for t in d.get('tracks', []):
    if not t.get('is_video'): continue
    t_idx = t.get('index')
    t_name = t.get('name')
    t_mute = t.get('mute')
    t_comp = t.get('composite_mode')
    for c in t.get('clips', []):
        s_ms = c.get('timeline_start_ms', 0)
        dur_ms = c.get('timeline_length_ms', 0)
        e_ms = s_ms + dur_ms
        if s_ms < 5000:
            c_name = c.get('name')
            fp = c.get('media_path')
            print(f"Vegas Trk {t_idx:2d} ({t_name:15s}) Mute={t_mute} Comp={t_comp} | [{s_ms:6.1f}ms -> {e_ms:6.1f}ms] dur={dur_ms:6.1f}ms | {c_name}")
