import os, subprocess
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
scratch_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_picks"
os.makedirs(scratch_dir, exist_ok=True)

font = None
for fp in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"]:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 18)
        break
if font is None: font = ImageFont.load_default()

# 1. 8114 jump detail (56s - 62s)
f_8114 = r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8114.MP4"
for s in [57.0, 58.0, 58.5, 59.0, 59.5, 60.0]:
    out_p = os.path.join(scratch_dir, f"8114_{s:.1f}s.jpg")
    cmd = ["ffmpeg", "-y", "-ss", str(s), "-i", f_8114, "-vframes", "1", "-vf", "scale=720:-1", "-q:v", "3", out_p]
    subprocess.run(cmd, capture_output=True)

# 2. 0060 board POV detail (154s - 159s)
f_0060 = r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\DJI_20260805072448_0060_D_ABD.MP4"
for s in [154.0, 155.0, 156.0, 157.0, 158.0]:
    out_p = os.path.join(scratch_dir, f"0060_{s:.1f}s.jpg")
    cmd = ["ffmpeg", "-y", "-ss", str(s), "-i", f_0060, "-vframes", "1", "-vf", "scale=720:-1", "-q:v", "3", out_p]
    subprocess.run(cmd, capture_output=True)

print("Extracted detailed frames for top picks")
