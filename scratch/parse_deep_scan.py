import re
import json

with open(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix F2 and control characters
fixed = re.sub(r':\s*F[0-9]+', ': 0.0', content)
fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: ' ' if m.group() not in '\r\n\t' else m.group(), fixed)

data = json.loads(fixed, strict=False)

video_events = []
tracks = data.get('tracks', [])
print(f"Project: {data.get('project_name')}")
print(f"Total tracks: {len(tracks)}")

for t in tracks:
    if not t.get('is_video'):
        continue
    t_name = t.get('name', 'Untitled')
    t_idx = t.get('index')
    events = t.get('events', [])
    for ev in events:
        m_path = ev.get('media_path', '')
        ev_name = ev.get('name', '')
        start_ms = ev.get('timeline_start_ms', 0)
        len_ms = ev.get('timeline_length_ms', 0)
        video_events.append({
            'track_index': t_idx,
            'track_name': t_name,
            'name': ev_name,
            'media_path': m_path,
            'start_ms': start_ms,
            'len_ms': len_ms
        })

print(f"Total video events placed on timeline in deep scan: {len(video_events)}")

unique_media = set(e['media_path'] for e in video_events if e['media_path'])
print(f"Unique media paths on timeline: {len(unique_media)}")
for p in sorted(list(unique_media))[:20]:
    print("  ", p)
