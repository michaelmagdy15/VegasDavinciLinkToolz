import sys
sys.stdout.reconfigure(encoding='utf-8')
import re, json

with open(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

fixed = re.sub(r':\s*F[0-9]+', ': 0.0', text)
fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: ' ' if m.group() not in '\r\n\t' else m.group(), fixed)
data = json.loads(fixed, strict=False)

print("=== ALL VIDEO EVENTS FROM 35s TO 50s ===")
for t in data.get('tracks', []):
    if not t.get('is_video'): continue
    t_name = t.get('name', 'Untitled')
    t_idx = t.get('index')
    for ev in t.get('events', []):
        start = ev.get('timeline_start_ms', 0)
        end = start + ev.get('timeline_length_ms', 0)
        if (start < 50000 and end > 35000):
            print(f"Track #{t_idx} [{t_name}]: '{ev.get('name')}' | {start/1000:.2f}s -> {end/1000:.2f}s | file={ev.get('media_path')}")
