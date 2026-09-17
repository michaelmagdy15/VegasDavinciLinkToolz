import os
from PIL import Image, ImageDraw, ImageFont

p = r'c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_sony_vertical'
artifacts_dir = r'C:\Users\Mi5a\.gemini\antigravity-ide\brain\3b4eacf0-7356-4382-87e3-0f14f5c19dec'

# Current blurry frame from Vegas at 00:00:42;07
# AbdraFilms-A7s20260804_9212 around the offset
cur_frame = r'c:\Users\Mi5a\VegasDavinciLinkTool\scratch\scout_transition\current_blurry.jpg'

candidates = [
    ('Current Blurry (9212)', cur_frame, 'Soft silhouette / hazy water chop'),
    ('Option A: A7IV 8122 @ 12.5s', os.path.join(p, 'A7IV_8122_12.5s.jpg'), 'Ultra-sharp speed carve, rooster spray'),
    ('Option B: A7IV 8116 @ 8.0s', os.path.join(p, 'A7IV_8116_8.0s.jpg'), 'Crisp rider power turn'),
    ('Option C: A7IV 8120 @ 2.0s', os.path.join(p, 'A7IV_8120_2.0s.jpg'), 'Dynamic action carve in turquoise water'),
    ('Option D: Dahab 0009 @ 69.5s', os.path.join(p, 'Dahab_0009_69.5s.jpg'), 'Vibrant blue lagoon aerial boost'),
    ('Option E: Hurghada 8230 @ 71.5s', os.path.join(p, 'Hurghada_8230_71.5s.jpg'), 'Athletic board-grab jump'),
]

# Create comparison grid (6 vertical frames: 2 rows of 3 columns)
card_w = 360
card_h = 640
padding = 20
header_h = 70
label_h = 80

total_w = 3 * card_w + 4 * padding
total_h = header_h + 2 * (card_h + label_h) + 3 * padding

grid = Image.new('RGB', (total_w, total_h), (18, 20, 24))
draw = ImageDraw.Draw(grid)

font_title = None
font_label = None
font_sub = None
for fp in ['C:\\Windows\\Fonts\\arialbd.ttf', 'C:\\Windows\\Fonts\\segoeuib.ttf']:
    if os.path.exists(fp):
        font_title = ImageFont.truetype(fp, 26)
        font_label = ImageFont.truetype(fp, 20)
        break
for fp in ['C:\\Windows\\Fonts\\arial.ttf', 'C:\\Windows\\Fonts\\segoeui.ttf']:
    if os.path.exists(fp):
        font_sub = ImageFont.truetype(fp, 15)
        break

if not font_title:
    font_title = font_label = font_sub = ImageFont.load_default()

# Header
draw.text((padding, 15), "VERTICAL 9:16 CANDIDATES: 00:00:42;07 (Markers 10 - 11)", fill=(255, 200, 40), font=font_title)
draw.text((padding, 45), "Replacing the 0.93s blurry cut of 9212 between Mid-Air Jump (8114) and Kiteloop Landing (9230)", fill=(180, 190, 200), font=font_sub)

for idx, (title, img_path, desc) in enumerate(candidates):
    row = idx // 3
    col = idx % 3
    
    x = padding + col * (card_w + padding)
    y = header_h + padding + row * (card_h + label_h + padding)
    
    if os.path.exists(img_path):
        im = Image.open(img_path)
        # resize to fit card_w x card_h
        im_resized = im.resize((card_w, card_h), Image.Resampling.LANCZOS)
        grid.paste(im_resized, (x, y))
    else:
        draw.rectangle([x, y, x + card_w, y + card_h], fill=(40, 40, 40))
        draw.text((x + 20, y + card_h // 2), "Frame Missing", fill=(200, 200, 200), font=font_label)
    
    # Border
    border_color = (200, 50, 50) if idx == 0 else ((40, 200, 120) if idx == 1 else (60, 80, 100))
    draw.rectangle([x, y, x + card_w, y + card_h], outline=border_color, width=3)
    
    # Label bar below
    label_y = y + card_h + 8
    draw.text((x, label_y), title, fill=(255, 255, 255) if idx != 0 else (255, 120, 120), font=font_label)
    draw.text((x, label_y + 26), desc, fill=(170, 180, 190), font=font_sub)

out_comp = os.path.join(artifacts_dir, "vertical_replacement_candidates_42s.jpg")
grid.save(out_comp, quality=92)
print("Saved comparison to:", out_comp)
