import os
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec"
stills_dir = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\stills"

shots_info = [
    {
        "id": 1,
        "tc": "00:00:13:21 (13.7s)",
        "client_request": "Replace slow beach preparation b-roll",
        "orig_title": "Original: 9209 (Slow Kite Setup on Sand)",
        "new_title": "Replacement: 9198 (Dynamic Kite Pumping)"
    },
    {
        "id": 2,
        "tc": "00:00:26:12 (26.4s)",
        "client_request": "Overexposed water glare / sun blowout",
        "orig_title": "Original: 0013_D (Overexposed Glare)",
        "new_title": "Replacement: 0014_D (Balanced Sun Drone)"
    },
    {
        "id": 3,
        "tc": "00:00:32:25 (32.8s)",
        "client_request": "Too much shoreline resort buildings",
        "orig_title": "Original: 0068_D (Resort Shoreline)",
        "new_title": "Replacement: 0001_D (Pure Blue Lagoon Open Water)"
    },
    {
        "id": 4,
        "tc": "00:00:33:24 (33.8s)",
        "client_request": "Too much resort bungalows / rooftops",
        "orig_title": "Original: 0004_D (Resort Rooftops)",
        "new_title": "Replacement: 0017_D (Low Water Chase)"
    },
    {
        "id": 5,
        "tc": "00:00:41:10 (41.3s)",
        "client_request": "Pacing transition too slow / flat",
        "orig_title": "Original: 9212 (Cruising on Water)",
        "new_title": "Replacement: 8226 (Hurghada Aerial Board-Off Jump)"
    },
    {
        "id": 6,
        "tc": "00:00:43:25 (43.8s)",
        "client_request": "Rider stumbling / losing balance",
        "orig_title": "Original: 9231 (Rider Stumble/Crash)",
        "new_title": "Replacement: 9230 (Landed Kiteloop & Spray Carve)"
    },
    {
        "id": 7,
        "tc": "00:00:47:12 (47.4s)",
        "client_request": "Boring distant static shot",
        "orig_title": "Original: 9382 (Distant Riding)",
        "new_title": "Replacement: 9214 (Explosive Water Spray at Lens)"
    }
]

# Try to find a system font
font = None
for font_path in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\calibrib.ttf", "C:\\Windows\\Fonts\\segoeui.ttf"]:
    if os.path.exists(font_path):
        try:
            font = ImageFont.truetype(font_path, 28)
            small_font = ImageFont.truetype(font_path, 20)
            break
        except Exception:
            pass

if font is None:
    font = ImageFont.load_default()
    small_font = font

target_h = 540

for s in shots_info:
    sid = s["id"]
    orig_p = os.path.join(stills_dir, f"shot_{sid}_orig.jpg")
    new_p = os.path.join(stills_dir, f"shot_{sid}_new.jpg")
    
    if not (os.path.exists(orig_p) and os.path.exists(new_p)):
        print(f"Skipping shot {sid}, missing stills: orig={os.path.exists(orig_p)} new={os.path.exists(new_p)}")
        continue

    img_o = Image.open(orig_p)
    img_n = Image.open(new_p)

    # Scale to target height preserving aspect ratio
    w_o = int(img_o.width * (target_h / img_o.height))
    img_o = img_o.resize((w_o, target_h), Image.Resampling.LANCZOS)

    w_n = int(img_n.width * (target_h / img_n.height))
    img_n = img_n.resize((w_n, target_h), Image.Resampling.LANCZOS)

    header_h = 80
    banner_h = 50
    total_w = w_o + w_n + 20
    total_h = target_h + header_h + banner_h

    canvas = Image.new("RGB", (total_w, total_h), (20, 24, 30))
    draw = ImageDraw.Draw(canvas)

    # Draw header banner
    draw.rectangle([(0, 0), (total_w, header_h)], fill=(12, 15, 20))
    title_text = f"SHOT {sid} @ {s['tc']} | Client Note: \"{s['client_request']}\""
    draw.text((20, 24), title_text, font=font, fill=(255, 215, 0))

    # Paste images
    canvas.paste(img_o, (0, header_h))
    canvas.paste(img_n, (w_o + 20, header_h))

    # Divider
    draw.rectangle([(w_o, header_h), (w_o + 20, header_h + target_h)], fill=(40, 45, 55))

    # Sub-banners below images
    banner_y = header_h + target_h
    draw.rectangle([(0, banner_y), (w_o, banner_y + banner_h)], fill=(45, 20, 20))
    draw.rectangle([(w_o + 20, banner_y), (total_w, banner_y + banner_h)], fill=(20, 50, 30))

    draw.text((15, banner_y + 12), f"[BEFORE] {s['orig_title']}", font=small_font, fill=(255, 180, 180))
    draw.text((w_o + 35, banner_y + 12), f"[AFTER] {s['new_title']}", font=small_font, fill=(180, 255, 180))

    out_file = os.path.join(artifacts_dir, f"comparison_shot_{sid}.jpg")
    canvas.save(out_file, quality=90)
    print(f"Saved comparison for Shot {sid}: {out_file}")
