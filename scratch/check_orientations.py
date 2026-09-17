import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, subprocess, json
from pathlib import Path

# Load index
with open(r'scratch\audit_proxies_to_hq.py') as f:
    pass

from core.live_bridge import load_manifest_json
p = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
data = load_manifest_json(str(p))

proxies = []
for t in data.get('tracks', []):
    for c in t.get('clips', []):
        mp = c.get('media_path')
        if mp and 'proxy' in mp.lower():
            proxies.append(mp)

proxies = sorted(set(proxies))

def probe_res(path):
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', path]
        r = subprocess.run(cmd, capture_output=True, text=True)
        d = json.loads(r.stdout)
        for s in d.get('streams', []):
            if s.get('codec_type') == 'video':
                # Check side data or tags for rotation
                rot = 0
                for side in s.get('side_data_list', []):
                    if 'rotation' in side:
                        rot = side['rotation']
                tags = s.get('tags', {})
                if 'rotate' in tags:
                    rot = int(tags['rotate'])
                return s.get('width'), s.get('height'), rot
    except Exception as e:
        return None, None, 0
    return None, None, 0

print(f"Comparing {len(proxies)} proxy vs HQ pairs...")
diff_orientation = []
for p in proxies:
    p_obj = Path(p)
    parent_dir = p_obj.parent.parent
    base = p_obj.stem
    hq = parent_dir / f"{base}.mp4"
    if not hq.exists():
        hq = parent_dir / f"{base}.mov"
    if not hq.exists():
        hq = parent_dir / f"{base}.MP4"

    if hq.exists():
        pw, ph, prot = probe_res(str(p_obj))
        hw, hh, hrot = probe_res(str(hq))
        # Check if aspect ratio flipped (e.g. vertical vs horizontal)
        p_is_vert = (pw is not None and ph is not None and ph > pw)
        h_is_vert = (hw is not None and hh is not None and hh > hw)
        if p_is_vert != h_is_vert or prot != hrot:
            diff_orientation.append({
                'base': base,
                'proxy': (pw, ph, prot),
                'hq': (hw, hh, hrot)
            })

print(f"Total with different orientation/dimensions: {len(diff_orientation)}")
for item in diff_orientation[:20]:
    print(f"Clip: {item['base']}")
    print(f"   Proxy: {item['proxy'][0]}x{item['proxy'][1]} (rot={item['proxy'][2]})")
    print(f"   HQ:    {item['hq'][0]}x{item['hq'][1]} (rot={item['hq'][2]})")
