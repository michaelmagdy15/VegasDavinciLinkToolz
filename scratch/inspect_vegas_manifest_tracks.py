import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app, load_manifest_json

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetCurrentTimeline()
print('Current Timeline in Resolve:', tl.GetName())
print('Current Timeline FPS:', tl.GetSetting('timelineFrameRate'))

m = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')
v_tracks = [t for t in m.get('tracks', []) if t.get('is_video')]
print(f'VEGAS video tracks: {len(v_tracks)}')
for i, t in enumerate(v_tracks):
    clips = t.get('clips', [])
    if clips:
        print(f'  VEGAS Track {i+1} "{t.get("name")}": {len(clips)} clips (mute: {t.get("mute", False)})')
