import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import subprocess
import json

dji_clips = [
    "DJI_20260727191357_0011_D_ABD", "DJI_20260727191804_0018_D_ABD", "DJI_20260804132644_0024_D_ABD",
    "DJI_20260804214749_0024_D_ABDRAFILMS", "DJI_20260805125817_0068_D_ABDRAFILMS",
    "DJI_20260806095235_0001_D_ABD", "DJI_20260806104427_0004_D_ABD", "DJI_20260806105138_0005_D_ABD",
    "DJI_20260806153417_0013_D_ABDRAFILMS", "DJI_20260820135006_0011_D_ABD", "DJI_20260820135737_0013_D_ABD",
    "DJI_20260820140232_0014_D_ABD", "DJI_20260820142651_0001_D", "DJI_20260820143132_0004_D",
    "DJI_20260820150311_0005_D", "DJI_20260820151353_0009_D", "DJI_20260820151712_0011_D",
    "DJI_20260820170229_0013_D", "DJI_20260820170404_0014_D", "DJI_20260820170727_0016_D",
    "DJI_20260820171112_0017_D", "DJI_20260820171439_0038_D"
]

found_paths = {}
for root, dirs, files in os.walk(r'F:\Arrow'):
    for f in files:
        base = os.path.splitext(f)[0]
        if base in dji_clips and f.lower().endswith(('.mp4', '.mov')):
            if 'proxy' not in root.lower():
                found_paths[base] = os.path.join(root, f)
            elif base not in found_paths:
                found_paths[base] = os.path.join(root, f)

for clip in dji_clips:
    p = found_paths.get(clip)
    if not p:
        print(f"{clip}: NOT FOUND")
        continue
    cmd = [
        r'C:\Program Files\FFmpeg\bin\ffprobe.exe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        p
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        j = json.loads(res.stdout)
        v = next(s for s in j.get('streams', []) if s.get('codec_type') == 'video')
        pix = v.get('pix_fmt')
        bits = v.get('bits_per_raw_sample')
        color_space = v.get('color_space')
        color_primaries = v.get('color_primaries')
        color_transfer = v.get('color_transfer')
        print(f"[{clip}] -> pix_fmt={pix}, bits={bits}, space={color_space}, primaries={color_primaries}, transfer={color_transfer}")
    except Exception as e:
        print(f"[{clip}] -> error: {e}")
