import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import load_manifest_json
from pathlib import Path

p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
d = load_manifest_json(str(p))

print("=== VEGAS CLIPS IN FIRST 3 SECONDS (0 - 3000ms) ===")
opening_clips = []
for t in d.get('tracks', []):
    t_idx = t.get('index')
    t_name = t.get('name')
    t_mute = t.get('mute')
    for c in t.get('clips', []):
        s = c.get('timeline_start_ms')
        l = c.get('timeline_length_ms')
        e = s + l
        if s < 3000:
            opening_clips.append((s, e, t_idx, t_name, t_mute, c))

opening_clips.sort(key=lambda x: (x[0], x[2]))

for s, e, t_idx, t_name, t_mute, c in opening_clips:
    print(f"[{s:6.1f}ms -> {e:6.1f}ms] (len {e-s:5.1f}ms) | Track {t_idx:2d} ({t_name:15s}, mute={t_mute}) | {c.get('name')} | fade_in={c.get('fade_in_ms')} fade_out={c.get('fade_out_ms')} gain={c.get('fade_gain')}")
