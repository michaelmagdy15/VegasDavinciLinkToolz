import os
import glob
from pathlib import Path
import sys
sys.path.insert(0, '.')
from core.live_bridge import load_manifest_json

json_path = Path.home() / '.timeline_bridge' / 'vegas_timeline.json'
data = load_manifest_json(str(json_path))

media_paths = set()
for t in data.get('tracks', []):
    for c in t.get('clips', []):
        mp = c.get('media_path')
        if mp:
            media_paths.add(mp)

proxy_paths = [mp for mp in media_paths if 'proxy' in mp.lower()]
print(f"Testing {len(proxy_paths)} proxy paths for High Quality counterparts...")

found_direct = 0
found_diff_ext = 0
found_search = 0
not_found = []

# Index F:\Arrow
print("Indexing F:\\Arrow files...")
arrow_index = {}
for root, dirs, files in os.walk(r'F:\Arrow'):
    for f in files:
        b = os.path.splitext(f)[0].lower()
        if b not in arrow_index:
            arrow_index[b] = []
        arrow_index[b].append(os.path.join(root, f))
print(f"Indexed {len(arrow_index)} base names in F:\\Arrow.")

sample_matches = []

for p in proxy_paths:
    p_obj = Path(p)
    parent_dir = p_obj.parent.parent  # up from .../Proxy
    base_name = p_obj.stem
    ext = p_obj.suffix

    # Option 1: Direct parent with same extension
    cand1 = parent_dir / p_obj.name
    # Option 2: Direct parent with .mp4 or .mov
    cand2_mp4 = parent_dir / f"{base_name}.mp4"
    cand2_mov = parent_dir / f"{base_name}.mov"
    cand2_MP4 = parent_dir / f"{base_name}.MP4"
    cand2_MOV = parent_dir / f"{base_name}.MOV"

    match = None
    if cand1.exists():
        match = str(cand1)
        found_direct += 1
    elif cand2_mp4.exists():
        match = str(cand2_mp4)
        found_diff_ext += 1
    elif cand2_mov.exists():
        match = str(cand2_mov)
        found_diff_ext += 1
    elif cand2_MP4.exists():
        match = str(cand2_MP4)
        found_diff_ext += 1
    elif cand2_MOV.exists():
        match = str(cand2_MOV)
        found_diff_ext += 1
    else:
        # Search index
        matches = [m for m in arrow_index.get(base_name.lower(), []) if 'proxy' not in m.lower() and m.lower().endswith(('.mp4', '.mov'))]
        if matches:
            match = matches[0]
            found_search += 1
        else:
            not_found.append(p)

    if match:
        sample_matches.append((p, match))

print(f"\n--- RESULTS ---")
print(f"Found directly in parent folder (same ext): {found_direct}")
print(f"Found in parent folder with different ext (.mp4/.mov): {found_diff_ext}")
print(f"Found in F:\\Arrow search: {found_search}")
print(f"Total High Quality Found: {found_direct + found_diff_ext + found_search} / {len(proxy_paths)}")
print(f"Not Found: {len(not_found)}")

if not_found:
    print("\nSample Not Found:")
    for nf in not_found[:5]:
        print(" ", nf)

print("\nSample Matches:")
for orig, hq in sample_matches[:5]:
    print(f" PROXY: {orig}\n    HQ: {hq}\n")
