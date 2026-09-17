import os
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
scratch_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch"

# Images
img1_p = os.path.join(scratch_dir, "scout_8121", "frame_26.5s.jpg")
img2_p = os.path.join(scratch_dir, "scout_picks", "8114_58.5s.jpg")
img3_p = os.path.join(scratch_dir, "scout_picks", "0060_156.0s.jpg")

im1 = Image.open(img1_p).resize((640, 360), Image.Resampling.LANCZOS)
im2 = Image.open(img2_p).resize((640, 360), Image.Resampling.LANCZOS)
im3 = Image.open(img3_p).resize((640, 360), Image.Resampling.LANCZOS)

# Create canvas: 3 columns, with header and banner
w, h = 640, 360
pad = 15
header_h = 90
footer_h = 70
total_w = (w * 3) + (pad * 4)
total_h = h + header_h + footer_h + pad

canvas = Image.new("RGB", (total_w, total_h), (18, 22, 28))
draw = ImageDraw.Draw(canvas)

font_title = None
font_label = None
for fp in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"]:
    if os.path.exists(fp):
        font_title = ImageFont.truetype(fp, 26)
        font_label = ImageFont.truetype(fp, 18)
        break
if font_title is None:
    font_title = ImageFont.load_default()
    font_label = font_title

# Header
draw.rectangle([(0, 0), (total_w, header_h)], fill=(10, 14, 18))
draw.text((pad, 15), "SHOT 7 REPLACEMENT OPTIONS | Brand Promo for ARROW Kitesurfing", font=font_title, fill=(255, 215, 0))
draw.text((pad, 50), "Replaces boring distant shot at 00:00:47:12 (~47.4s). All 3 options are 100% UNUSED 4K masters.", font=font_label, fill=(200, 210, 220))

# Option 1: 8121 Power Carve
x1 = pad
y = header_h + 10
canvas.paste(im1, (x1, y))
draw.rectangle([(x1, y + h), (x1 + w, y + h + footer_h)], fill=(25, 35, 45))
draw.text((x1 + 10, y + h + 10), "Option A: Aggressive Power Carve (A7 IV 4K)", font=font_title, fill=(100, 230, 255))
draw.text((x1 + 10, y + h + 42), "ARROW board clearly visible, intense spray, close-up dynamic action.", font=font_label, fill=(220, 230, 240))

# Option 2: 8114 Mid-Air Kiteloop
x2 = x1 + w + pad
canvas.paste(im2, (x2, y))
draw.rectangle([(x2, y + h), (x2 + w, y + h + footer_h)], fill=(25, 35, 45))
draw.text((x2 + 10, y + h + 10), "Option B: Mid-Air Kiteloop Jump (A7 IV 4K)", font=font_title, fill=(100, 255, 150))
draw.text((x2 + 10, y + h + 42), "High-energy athletic jump, rider flying high with board extended.", font=font_label, fill=(220, 230, 240))

# Option 3: 0060 Onboard Tip POV
x3 = x2 + w + pad
canvas.paste(im3, (x3, y))
draw.rectangle([(x3, y + h), (x3 + w, y + h + footer_h)], fill=(25, 35, 45))
draw.text((x3 + 10, y + h + 10), "Option C: Onboard Tip POV (Action Cam 4K)", font=font_title, fill=(255, 180, 100))
draw.text((x3 + 10, y + h + 42), "Mounted on ARROW board nose, intense water spray skimming surface.", font=font_label, fill=(220, 230, 240))

out_path = os.path.join(artifacts_dir, "shot7_top_candidates.jpg")
canvas.save(out_path, quality=90)
print("Saved Shot 7 comparison:", out_path)
