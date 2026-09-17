import os
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
scratch_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_transition"

# Original blurry frame
orig_blurry_p = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\stills\shot_5_orig.jpg"
# Wait, let's extract the exact frame at 42.5s from the timeline event 9212!
cmd = ["ffmpeg", "-y", "-ss", "4.0", "-i", r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9212.MP4", "-vframes", "1", "-vf", "scale=480:-1", "-q:v", "3", os.path.join(scratch_dir, "current_blurry.jpg")]
import subprocess
subprocess.run(cmd, capture_output=True)

files = [
    ("CURRENT (Blurry 9212)", os.path.join(scratch_dir, "current_blurry.jpg"), "Current out-of-focus cut"),
    ("Candidate 1: Water Spray Impact (9214 @ 24.2s)", os.path.join(scratch_dir, "spray_9214_24.2s.jpg"), "Explosive water sheet hitting lens"),
    ("Candidate 2: Water Spray Crash (9214 @ 40.5s)", os.path.join(scratch_dir, "spray_9214_alt_40.5s.jpg"), "Dynamic splash transition"),
    ("Candidate 3: Speed Carve (8122 @ 12.5s)", os.path.join(scratch_dir, "carve_8122_12.5s.jpg"), "Rider leaning hard in power carve"),
    ("Candidate 4: Close Carve (8122 @ 50.0s)", os.path.join(scratch_dir, "carve_8122_fast_50.0s.jpg"), "Sharp close-up body angle"),
    ("Candidate 5: Board Grab Jump (8230 @ 71.5s)", os.path.join(scratch_dir, "hurghada_boardgrab_71.5s.jpg"), "Athletic grab in turquoise water")
]

font = None
for fp in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"]:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 18)
        title_font = ImageFont.truetype(fp, 22)
        break
if font is None:
    font = ImageFont.load_default()
    title_font = font

w, h = 480, 270
pad = 12
header_h = 70
footer_h = 50
cols = 3
rows = 2
total_w = cols * w + (cols + 1) * pad
total_h = rows * (h + footer_h) + header_h + (rows + 1) * pad

canvas = Image.new("RGB", (total_w, total_h), (18, 22, 28))
draw = ImageDraw.Draw(canvas)

draw.rectangle([(0, 0), (total_w, header_h)], fill=(10, 14, 18))
draw.text((pad, 12), "REPLACEMENT CANDIDATES: 00:00:42;07 (Between Marker 10 & 11)", font=title_font, fill=(255, 215, 0))
draw.text((pad, 42), "Replacing the 0.93s blurry cut of 9212 between High-Flying Jump and Kiteloop Landing", font=font, fill=(200, 210, 220))

for idx, (title, img_p, sub) in enumerate(files):
    if not os.path.exists(img_p): continue
    im = Image.open(img_p).resize((w, h), Image.Resampling.LANCZOS)
    c = idx % cols
    r = idx // cols
    x = pad + c * (w + pad)
    y = header_h + pad + r * (h + footer_h + pad)
    
    canvas.paste(im, (x, y))
    
    box_color = (60, 20, 20) if idx == 0 else (25, 38, 50)
    draw.rectangle([(x, y + h), (x + w, y + h + footer_h)], fill=box_color)
    draw.text((x + 8, y + h + 6), title, font=font, fill=(255, 255, 255) if idx != 0 else (255, 150, 150))
    draw.text((x + 8, y + h + 28), sub, font=font, fill=(180, 200, 210))

out_path = os.path.join(artifacts_dir, "transition_replacement_candidates.jpg")
canvas.save(out_path, quality=90)
print("Saved comparison sheet:", out_path)
