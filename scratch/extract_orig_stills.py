import os, subprocess
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')
out_dir = r'c:\Users\Mi5a\VegasDavinciLinkTool\scratch\stills'

targets = [
    (1, 13700, "9209"),
    (2, 26400, "0013_D"),
    (3, 32830, "0068_D"),
    (4, 33800, "0004_D"),
    (5, 41330, "9212"),
    (6, 43830, "9231"),
    (7, 47400, "9382")
]

for sid, tms, hint in targets:
    for ti, t in enumerate(d.get('tracks', [])):
        if not t.get('is_video'): continue
        tname = (t.get('name') or '').lower()
        if any(b in tname for b in ['[adjustment]', 'film burn', 'filmburn', 'halation', 'lut', 'transiotions']):
            continue
        for ev in t.get('events', []):
            mpath = ev.get('media_path', '')
            if not mpath: continue
            st = ev.get('timeline_start_ms', 0)
            dur = ev.get('timeline_length_ms', 0)
            end = st + dur
            if st <= (tms + 300) and end >= (tms - 300):
                cname = ev.get('name', '')
                if hint.lower() in cname.lower() or hint.lower() in mpath.lower():
                    src_in = ev.get('source_in_ms', 0) / 1000.0
                    orig_out = os.path.join(out_dir, f"shot_{sid}_orig.jpg")
                    file_to_extract = mpath
                    if not os.path.exists(file_to_extract):
                        raw_candidate = mpath.replace(r"\Proxy\\", "\\").replace(".mov", ".MP4").replace(".MOV", ".MP4")
                        if os.path.exists(raw_candidate):
                            file_to_extract = raw_candidate
                    if os.path.exists(file_to_extract):
                        cmd = ["ffmpeg", "-y", "-ss", str(src_in), "-i", file_to_extract, "-vframes", "1", "-q:v", "3", orig_out]
                        subprocess.run(cmd, capture_output=True)
                        print(f"Shot {sid} extracted: {os.path.basename(orig_out)} (exists={os.path.exists(orig_out)})")
                    else:
                        print(f"Shot {sid} file not found: {os.path.basename(file_to_extract)}")
