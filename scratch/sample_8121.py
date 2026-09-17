import os, subprocess
from PIL import Image

f = r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8121.MP4"
out_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_8121"
os.makedirs(out_dir, exist_ok=True)

# Sample every 0.5s from 23.0 to 30.0
for s in [23.0, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 29.0]:
    out_p = os.path.join(out_dir, f"frame_{s:.1f}s.jpg")
    cmd = ["ffmpeg", "-y", "-ss", str(s), "-i", f, "-vframes", "1", "-vf", "scale=720:-1", "-q:v", "3", out_p]
    subprocess.run(cmd, capture_output=True)

print(f"Extracted frames from 8121: {len(os.listdir(out_dir))}")
