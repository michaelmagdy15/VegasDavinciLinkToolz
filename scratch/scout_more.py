import os, subprocess
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
scratch_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_more"
os.makedirs(scratch_dir, exist_ok=True)

font = None
for fp in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"]:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 18)
        break
if font is None: font = ImageFont.load_default()

clips_to_scout = [
    ("drone_0060", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\DJI_20260805072448_0060_D_ABD.MP4"),
    ("a7s_9119", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260727_9119.MP4"),
    ("a7iv_8114", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8114.MP4"),
    ("drone_dahab_0015", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\youssef blue lagoon\DJI_20260820173245_0015_D_ABD.MP4")
]

for name, path in clips_to_scout:
    if not os.path.exists(path):
        print("Not found:", path)
        continue
    cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    dur = float(subprocess.check_output(cmd_dur).decode().strip())
    
    # Sample 8 frames across clip
    step = max(2.0, dur / 9.0)
    timestamps = [step * i for i in range(1, 9)]
    
    frames = []
    for ts in timestamps:
        out_jpg = os.path.join(scratch_dir, f"{name}_{ts:.1f}s.jpg")
        cmd = ["ffmpeg", "-y", "-ss", str(ts), "-i", path, "-vframes", "1", "-vf", "scale=360:-1", "-q:v", "4", out_jpg]
        subprocess.run(cmd, capture_output=True)
        if os.path.exists(out_jpg):
            im = Image.open(out_jpg)
            im = im.resize((320, 180), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([(0, 0), (140, 26)], fill=(0, 0, 0, 180))
            d.text((5, 3), f"{name} {ts:.1f}s", font=font, fill=(255, 255, 0))
            frames.append(im)
            
    if frames:
        cols = 4
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 320, rows * 180), (15, 15, 20))
        for idx, f in enumerate(frames):
            r = idx // cols
            c = idx % cols
            sheet.paste(f, (c * 320, r * 180))
        sheet_path = os.path.join(artifacts_dir, f"candidate_{name}.jpg")
        sheet.save(sheet_path, quality=85)
        print(f"Created candidate sheet: {sheet_path}")
