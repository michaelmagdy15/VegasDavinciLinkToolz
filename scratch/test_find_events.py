import sys
sys.stdout.reconfigure(encoding='utf-8')
import re, json

with open(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

fixed = re.sub(r':\s*F[0-9]+', ': 0.0', text)
fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: ' ' if m.group() not in '\r\n\t' else m.group(), fixed)
data = json.loads(fixed, strict=False)

def test_find(target_ms, hint):
    fallback = None
    for t in data.get('tracks', []):
        if not t.get('is_video'): continue
        tname = (t.get('name') or '').lower()
        if '[adjustment]' in tname or 'film burn' in tname or 'filmburn' in tname: continue
        
        for ev in t.get('events', []):
            start = ev.get('timeline_start_ms', 0)
            end = start + ev.get('timeline_length_ms', 0)
            if start <= (target_ms + 200) and end >= (target_ms - 200):
                cname = ev.get('name') or ''
                if hint and hint.lower() in cname.lower():
                    return t.get('index'), t.get('name'), ev
                if fallback is None and not ev.get('mute'):
                    fallback = (t.get('index'), t.get('name'), ev)
    return fallback

print("Target 41.3s:")
r41 = test_find(41330, "")
if r41:
    print(f"  Track #{r41[0]} [{r41[1]}]: '{r41[2].get('name')}' | start={r41[2].get('timeline_start_ms')/1000:.2f}s, end={(r41[2].get('timeline_start_ms')+r41[2].get('timeline_length_ms'))/1000:.2f}s | file='{r41[2].get('media_path')}'")
else:
    print("  None")

print("Target 43.8s:")
r43 = test_find(43830, "")
if r43:
    print(f"  Track #{r43[0]} [{r43[1]}]: '{r43[2].get('name')}' | start={r43[2].get('timeline_start_ms')/1000:.2f}s, end={(r43[2].get('timeline_start_ms')+r43[2].get('timeline_length_ms'))/1000:.2f}s | file='{r43[2].get('media_path')}'")
else:
    print("  None")

print("Target 47.4s:")
r47 = test_find(47400, "8192")
if r47:
    print(f"  Track #{r47[0]} [{r47[1]}]: '{r47[2].get('name')}' | start={r47[2].get('timeline_start_ms')/1000:.2f}s, end={(r47[2].get('timeline_start_ms')+r47[2].get('timeline_length_ms'))/1000:.2f}s | file='{r47[2].get('media_path')}'")
else:
    print("  None")
