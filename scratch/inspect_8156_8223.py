import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import get_resolve_app, load_manifest_json
from pathlib import Path

resolve = get_resolve_app()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()

d = load_manifest_json(str(Path.home() / '.timeline_bridge' / 'vegas_timeline.json'))

for t in d.get('tracks', []):
    for c in t.get('clips', []):
        if '8156' in c.get('name', '') or '8223' in c.get('name', ''):
            print(f"VEGAS Track {t.get('index')} ({t.get('name')}):")
            print(f"  Clip: {c.get('name')}")
            print(f"  Timeline start: {c.get('timeline_start_ms')}ms, len: {c.get('timeline_length_ms')}ms")
            print(f"  Source in: {c.get('source_in_ms')}ms")
            print(f"  Fade in: {c.get('fade_in_ms')}ms, Fade out: {c.get('fade_out_ms')}ms, Gain: {c.get('fade_gain')}")
