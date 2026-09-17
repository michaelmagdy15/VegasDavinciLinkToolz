import sys
sys.path.insert(0, r'c:\Users\Mi5a\VegasDavinciLinkTool')
from core.live_bridge import import_timeline_from_json
from pathlib import Path

json_path = str(Path.home() / '.timeline_bridge' / 'vegas_timeline.json')
print(f"Running Live Link Sync from: {json_path}")
ok = import_timeline_from_json(json_path)
print(f"Import result: {ok}")
