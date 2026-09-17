import os
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
in_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_8121"

font = None
for fp in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"]:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 18)
        break
if font is None: font = ImageFont.load_default()

frames = sorted(os.listdir(in_dir))
imgs = []
for fn in frames:
    p = os.path.join(in_dir, fn)
    im = Image.open(p)
    im = im.resize((360, 202), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(im)
    ts = fn.replace("frame_", "").replace(".jpg", "")
    d.rectangle([(0, 0), (100, 26)], fill=(0, 0, 0, 200))
    d.text((5, 3), ts, font=font, fill=(255, 255, 0))
    imgs.append(im)

cols = 4
rows = (len(imgs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 360, rows * 202), (20, 20, 25))
for idx, im in enumerate(imgs):
    r = idx // cols
    c = idx % cols
    sheet.paste(im, (c * 360, r * 202))

out_file = os.path.join(artifacts_dir, "scout_8121_detail.jpg")
sheet.save(out_file, quality=90)
print("Saved 8121 detail sheet:", out_file)
