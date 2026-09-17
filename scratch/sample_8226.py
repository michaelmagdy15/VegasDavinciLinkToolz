import os, subprocess
from PIL import Image

f = r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\kiting hurghada\AbdraFilms-A7IV20260806_8226.MP4"
out_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_8226"
os.makedirs(out_dir, exist_ok=True)

# Sample every 2 seconds from 0 to 126
for s in range(0, 126, 2):
    out_p = os.path.join(out_dir, f"frame_{s:03d}s.jpg")
    cmd = ["ffmpeg", "-y", "-ss", str(s), "-i", f, "-vframes", "1", "-vf", "scale=480:-1", "-q:v", "5", out_p]
    subprocess.run(cmd, capture_output=True)

print(f"Extracted {len(os.listdir(out_dir))} frames from 8226")
