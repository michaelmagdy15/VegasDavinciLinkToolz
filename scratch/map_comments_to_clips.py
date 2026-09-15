import sys
sys.stdout.reconfigure(encoding='utf-8')
import re, json

# Parse vegas_deep_scan.json to get exact timeline events and their start/length ms
with open(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

fixed = re.sub(r':\s*F[0-9]+', ': 0.0', text)
fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: ' ' if m.group() not in '\r\n\t' else m.group(), fixed)
data = json.loads(fixed, strict=False)

fps = 29.97

def tc_to_ms(tc_str):
    # format HH:MM:SS:FF
    parts = [float(p) for p in tc_str.split(':')]
    h, m, s, f = parts[0], parts[1], parts[2], parts[3]
    total_s = h * 3600 + m * 60 + s + (f / fps)
    return total_s * 1000.0

comments = [
    ("00:00:01:06", "dont like this effect honestly"),
    ("00:00:13:21", "replace shot"),
    ("00:00:26:12", "overexposed? if cant be fixed remove"),
    ("00:00:32:12", "fix the horizon"),
    ("00:00:32:25", "too much buildings , lets replace the shot"),
    ("00:00:33:24", "replace too , too much rooftop"),
    ("00:00:41:10", "replace shot"),
    ("00:00:43:25", "replace , he is basically fallin"),
    ("00:00:47:12", "boring shot"),
    ("00:01:02:27", "feh moshkla f el slo mo")
]

print("=== MAPPING CLIENT COMMENTS TO TIMELINE CLIPS ===")
for tc, comment in comments:
    ms = tc_to_ms(tc)
    matching_events = []
    for t in data.get('tracks', []):
        if not t.get('is_video'): continue
        t_name = t.get('name', 'Untitled')
        t_idx = t.get('index')
        for ev in t.get('events', []):
            start = ev.get('timeline_start_ms', 0)
            length = ev.get('timeline_length_ms', 0)
            end = start + length
            if start <= ms <= end:
                matching_events.append({
                    'track_idx': t_idx,
                    'track_name': t_name,
                    'name': ev.get('name'),
                    'media_path': ev.get('media_path'),
                    'start_ms': start,
                    'end_ms': end
                })
    print(f"\nTimecode: {tc} (~{ms/1000:.2f}s) | Comment: \"{comment}\"")
    if not matching_events:
        print("  No active video event at this exact ms.")
    for me in matching_events:
        print(f"  -> Track #{me['track_idx']} [{me['track_name']}]: \"{me['name']}\"")
        if me['media_path']:
            print(f"     File: {me['media_path']}")
