import os, subprocess
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
scratch_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout"
os.makedirs(scratch_dir, exist_ok=True)

font = None
for fp in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"]:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 20)
        break
if font is None: font = ImageFont.load_default()

def create_contact_sheet(clip_path, name, timestamps, cols=4):
    frames = []
    for ts in timestamps:
        out_jpg = os.path.join(scratch_dir, f"{name}_{ts:.1f}s.jpg")
        cmd = ["ffmpeg", "-y", "-ss", str(ts), "-i", clip_path, "-vframes", "1", "-q:v", "4", out_jpg]
        subprocess.run(cmd, capture_output=True)
        if os.path.exists(out_jpg):
            im = Image.open(out_jpg)
            im = im.resize((320, 180), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([(0, 0), (120, 30)], fill=(0, 0, 0, 180))
            d.text((5, 5), f"{ts:.1f}s", font=font, fill=(255, 255, 0))
            frames.append(im)
    
    if not frames: return None
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 320, rows * 180), (15, 15, 20))
    for idx, f in enumerate(frames):
        r = idx // cols
        c = idx % cols
        sheet.paste(f, (c * 320, r * 180))
    
    sheet_path = os.path.join(artifacts_dir, f"scout_{name}.jpg")
    sheet.save(sheet_path, quality=85)
    print(f"Generated contact sheet: {sheet_path}")
    return sheet_path

# 1. 9198: 21.5s -> Sample every 2 seconds
create_contact_sheet(
    r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna brolls\AbdraFilms-A7s20260804_9198.MP4",
    "9198_kite_pumping",
    [0.5, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
)

# 2. 8226: 127s -> Sample every 8 seconds across clip
create_contact_sheet(
    r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\kiting hurghada\AbdraFilms-A7IV20260806_8226.MP4",
    "8226_aerial_jump",
    [2.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 118.0]
)

# 3. 9214: 49.5s -> Sample every 4 seconds
create_contact_sheet(
    r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9214.MP4",
    "9214_water_spray",
    [1.0, 4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0, 44.0]
)

# 4. 0001_D: 95.7s -> Sample every 8 seconds
create_contact_sheet(
    r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820142651_0001_D.MP4",
    "0001_D_blue_lagoon",
    [2.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
)

# 5. 0014_D: 157.8s -> Sample every 12 seconds
create_contact_sheet(
    r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820170404_0014_D.MP4",
    "0014_D_drone_sun",
    [5.0, 20.0, 35.0, 50.0, 65.0, 80.0, 95.0, 110.0, 125.0, 140.0]
)
