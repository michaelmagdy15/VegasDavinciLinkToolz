import os
import sys
from pathlib import Path

# Add repo root to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "Users" / "Mi5a" / "VegasDavinciLinkTool"
if not repo_root.exists():
    repo_root = Path(r"C:\Users\Mi5a\VegasDavinciLinkTool")
sys.path.insert(0, str(repo_root))

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.live_bridge import xml_to_timeline_json, import_timeline_from_json

xml_path = r"C:\Users\Mi5a\Documents\Kiting Hurghada_Untitled Timeline.xml"
print("1. Converting VEGAS timeline to JSON manifest...")
json_path = xml_to_timeline_json(xml_path)
print("   Manifest saved to:", json_path)

print("\n2. Connecting to running DaVinci Resolve instance...")
success = import_timeline_from_json(json_path, log_fn=print)
print("\n3. Result:", "SUCCESS" if success else "FAILED")
