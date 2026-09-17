import math
import os
import colorsys
from pathlib import Path

def rgb_to_hsv(r, g, b):
    return colorsys.rgb_to_hsv(r, g, b)

def hsv_to_rgb(h, s, v):
    return colorsys.hsv_to_rgb(h, s, v)

def s_curve(x):
    # Smooth cinematic S-curve: deepens blacks, soft highlight shoulder
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    # Hermite interpolation / soft contrast
    # Midpoint around 0.45
    return x * x * (3.0 - 2.0 * x) * 0.3 + (1.0 / (1.0 + math.exp(-6.0 * (x - 0.45)))) * 0.7

def apply_vibrant_turquoise_look(r, g, b):
    """Transform normalized Rec.709 colors into 'Vibrant Turquoise Lagoon & Golden Sun Pop'."""
    # Clamp input
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    
    h, s, v = rgb_to_hsv(r, g, b)
    h_deg = h * 360.0
    
    # 1. Turquoise / Ocean / Sky Enhancement (Hue 160 to 240)
    # Red Sea / Dahab lagoon: shift deep blues (210-230) toward turquoise/cyan (185-195)
    if 150.0 <= h_deg <= 245.0:
        # Distance from target cyan (185 deg)
        dist = abs(h_deg - 200.0)
        weight = max(0.0, 1.0 - (dist / 45.0))
        # Shift hue towards 185 (cyan/turquoise)
        h_deg = h_deg * (1.0 - 0.35 * weight) + 185.0 * (0.35 * weight)
        # Boost saturation of the lagoon
        s = min(1.0, s * (1.0 + 0.28 * weight))
        # Slightly enhance luminance of turquoise water for crystalline sparkle
        v = min(1.0, v * (1.0 + 0.06 * weight))
    
    # 2. Skin Tone Protection & Warmth (Hue 15 to 45 deg)
    elif 15.0 <= h_deg <= 50.0:
        dist_skin = abs(h_deg - 30.0)
        weight_skin = max(0.0, 1.0 - (dist_skin / 25.0))
        # Keep hue anchored to natural skin tone (30 deg)
        h_deg = h_deg * (1.0 - 0.15 * weight_skin) + 28.0 * (0.15 * weight_skin)
        # Gentle healthy saturation bump
        s = min(1.0, s * (1.0 + 0.08 * weight_skin))
    
    # 3. Vivid Kite Colors (Reds: 340-15, Yellows: 50-70, Greens: 70-140)
    elif (h_deg >= 340.0 or h_deg <= 15.0) or (50.0 <= h_deg <= 140.0):
        # Commercial pop for kite gear and beach elements
        s = min(1.0, s * 1.15)

    h = (h_deg % 360.0) / 360.0
    r, g, b = hsv_to_rgb(h, s, v)
    
    # 4. Cinematic Contrast & Golden Sun Rolloff
    # Contrast curve applied to RGB channels
    # S-curve with rich blacks
    r = math.pow(r, 1.05)
    g = math.pow(g, 1.05)
    b = math.pow(b, 1.08) # slight cool shadow depth
    
    # Golden highlight warmth (sun on water & skin highlights)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lum > 0.65:
        hl_weight = (lum - 0.65) / 0.35
        # Warm golden push in top highlights
        r = min(1.0, r + 0.035 * hl_weight)
        g = min(1.0, g + 0.015 * hl_weight)
        b = max(0.0, b - 0.020 * hl_weight)
    
    # Soft highlight rolloff (prevent harsh clipping)
    r = min(1.0, max(0.0, r))
    g = min(1.0, max(0.0, g))
    b = min(1.0, max(0.0, b))
    
    return r, g, b

def process_cube_lut(src_cube_path: str, dst_cube_path: str, title: str):
    """Read a base 3D LUT, transform all output RGBs with the creative look, and save new LUT."""
    print(f"Processing: {src_cube_path} -> {dst_cube_path}")
    with open(src_cube_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    out_lines = [
        f'TITLE "{title}"\n',
        '# Color Graded by VegasDavinciLinkTool\n',
        '# Look: Vibrant Turquoise Lagoon & Golden Sun Pop\n',
    ]
    
    lut_size = 33
    in_data = False
    
    for line in lines:
        sline = line.strip()
        if not sline or sline.startswith('#'):
            continue
        if sline.startswith('LUT_3D_SIZE'):
            lut_size = int(sline.split()[1])
            out_lines.append(f"LUT_3D_SIZE {lut_size}\n\n")
            in_data = True
            continue
        if sline.startswith('TITLE') or sline.startswith('DOMAIN_'):
            continue
            
        if in_data:
            parts = sline.split()
            if len(parts) == 3:
                try:
                    r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
                    nr, ng, nb = apply_vibrant_turquoise_look(r, g, b)
                    out_lines.append(f"{nr:.6f} {ng:.6f} {nb:.6f}\n")
                except ValueError:
                    out_lines.append(line)
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)
            
    with open(dst_cube_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)
    print(f"[OK] Generated: {dst_cube_path} ({os.path.getsize(dst_cube_path)} bytes)")

if __name__ == '__main__':
    lut_dir = Path(os.environ.get('PROGRAMDATA', r'C:\ProgramData')) / 'Blackmagic Design' / 'DaVinci Resolve' / 'Support' / 'LUT' / 'VEGAS_Imported'
    
    sony_src = lut_dir / 'Pike_SL3_0-5_Skin1.cube'
    sony_dst = lut_dir / 'Arrow_Vibrant_Turquoise_Sony_A7.cube'
    process_cube_lut(str(sony_src), str(sony_dst), 'Arrow Vibrant Turquoise - Sony A7 IV/S3')
    
    dji_src = lut_dir / 'DJI Mini 4 Pro D-Log M to Rec.709 V1_.cube'
    dji_dst = lut_dir / 'Arrow_Vibrant_Turquoise_DJI_Drone.cube'
    process_cube_lut(str(dji_src), str(dji_dst), 'Arrow Vibrant Turquoise - DJI Drone')
