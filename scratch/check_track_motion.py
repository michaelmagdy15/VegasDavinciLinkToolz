import sys
sys.stdout.reconfigure(encoding='utf-8')
import re, json

with open(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

fixed = re.sub(r':\s*F[0-9]+', ': 0.0', text)
fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: ' ' if m.group() not in '\r\n\t' else m.group(), fixed)
data = json.loads(fixed, strict=False)

for t in data.get('tracks', []):
    tname = t.get('name', '')
    tm = t.get('track_motion', {})
    events = t.get('events', [])
    rot_events = []
    for ev in events:
        pk = ev.get('pan_crop_keyframes', [])
        for k in pk:
            if abs(k.get('rotation', 0.0)) > 0.01:
                rot_events.append((ev.get('name'), k.get('rotation')))
    if '90' in tname or tm or rot_events:
        print(f"Track #{t.get('index')} [{tname}]:")
        if tm:
            print(f"   Track Motion: {tm}")
        if rot_events:
            print(f"   Rotated Pan/Crop Events: {rot_events}")
