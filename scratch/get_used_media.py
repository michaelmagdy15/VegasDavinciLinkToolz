import sys, os
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')

used_files = set()
for t in d.get('tracks', []):
    for ev in t.get('events', []):
        mpath = ev.get('media_path', '')
        if mpath:
            # normalize filename
            fn = os.path.basename(mpath).lower()
            # remove proxy suffix if any
            fn = fn.replace('.mov', '').replace('.mp4', '')
            used_files.add(fn)

print(f"Total used unique media base names in project: {len(used_files)}")
# Write to a file for easy lookup
with open(r'c:\Users\Mi5a\VegasDavinciLinkTool\scratch\used_media_names.txt', 'w', encoding='utf-8') as f:
    for name in sorted(used_files):
        f.write(name + '\n')
print("Saved used media list to scratch/used_media_names.txt")
