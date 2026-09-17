import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from pathlib import Path
from core.live_bridge import load_manifest_json

json_path = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
data = load_manifest_json(str(json_path))

for idx, t in enumerate(data.get('tracks', [])):
    tname = t.get('name', '')
    if 'lut' in tname.lower() or t.get('is_adjustment', False):
        print(f"Track #{idx} [{tname}], is_adj={t.get('is_adjustment')}, clips_count={len(t.get('clips', []))}")
        for c in t.get('clips', []):
            print(f"   Clip: '{c.get('name')}', path: '{c.get('media_path')}'")
