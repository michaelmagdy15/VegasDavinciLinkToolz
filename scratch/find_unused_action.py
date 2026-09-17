import os, sys

with open(r'c:\Users\Mi5a\VegasDavinciLinkTool\scratch\used_media_names.txt', 'r', encoding='utf-8') as f:
    used = set(line.strip().lower() for line in f if line.strip())

candidate_dirs = [
    r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting",
    r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\kiting hurghada",
    r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\youssef blue lagoon",
    r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon",
]

unused_clips = []
for d in candidate_dirs:
    if not os.path.exists(d): continue
    for f in os.listdir(d):
        if not f.upper().endswith(('.MP4', '.MOV')) or f.startswith('._'):
            continue
        base = os.path.splitext(f)[0].lower()
        if base not in used:
            fp = os.path.join(d, f)
            sz_mb = os.path.getsize(fp) / 1024 / 1024
            # We want substantive clips, say > 200MB (meaning good length and high bitrate 4K)
            if sz_mb > 200:
                unused_clips.append((sz_mb, fp, f, os.path.basename(d)))

unused_clips.sort(key=lambda x: x[0], reverse=True)
print(f"Found {len(unused_clips)} large unused 4K clips!")
for sz, fp, f, folder in unused_clips[:25]:
    print(f"{sz:6.1f} MB | {folder} | {f}")
