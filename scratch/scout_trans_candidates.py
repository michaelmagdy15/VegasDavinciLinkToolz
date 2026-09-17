import os, subprocess
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
scratch_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_transition"
os.makedirs(scratch_dir, exist_ok=True)

# Candidates for a ~1-second punchy, sharp transition between jump and landing:
# 1. 8121 @ 26.5s - spray carve (if not already ending shot) OR 8122
# 2. 9214 @ 24.5s - explosive water spray hitting the lens (super dynamic 1s transition!)
# 3. 8119 / 8120 in sokhna kiting
# 4. 9248 / 9249
# 5. dahab 0009 @ 69.5s - sandspit jump

candidates = [
    ("spray_9214", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9214.MP4", 24.2),
    ("spray_9214_alt", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9214.MP4", 40.5),
    ("carve_8122", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8122.MP4", 12.5),
    ("carve_8122_fast", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8122.MP4", 50.0),
    ("dahab_jump", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\youssef blue lagoon\AbdraFilms-A7s20260820_0009.MP4", 69.5),
    ("hurghada_boardgrab", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\kiting hurghada\AbdraFilms-A7IV20260806_8230.MP4", 71.5),
]

font = None
for fp in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"]:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 18)
        break
if font is None: font = ImageFont.load_default()

extracted = []
for name, path, ts in candidates:
    if not os.path.exists(path): continue
    out_p = os.path.join(scratch_dir, f"{name}_{ts:.1f}s.jpg")
    cmd = ["ffmpeg", "-y", "-ss", str(ts), "-i", path, "-vframes", "1", "-vf", "scale=480:-1", "-q:v", "3", out_p]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(out_p):
        extracted.append((name, out_p, ts))

print(f"Extracted {len(extracted)} candidate frames")
