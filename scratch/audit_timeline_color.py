import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import re
import json
import xml.etree.ElementTree as ET
import subprocess

timeline_clips = [
    # Sony A7 IV
    "AbdraFilms-A7IV20260804_8116", "AbdraFilms-A7IV20260804_8117", "AbdraFilms-A7IV20260804_8118",
    "AbdraFilms-A7IV20260804_8119", "AbdraFilms-A7IV20260804_8120", "AbdraFilms-A7IV20260804_8123",
    "AbdraFilms-A7IV20260804_8124", "AbdraFilms-A7IV20260804_8127", "AbdraFilms-A7IV20260805_8156",
    "AbdraFilms-A7IV20260805_8181", "AbdraFilms-A7IV20260805_8187", "AbdraFilms-A7IV20260805_8188",
    "AbdraFilms-A7IV20260805_8192", "AbdraFilms-A7IV20260806_8216", "AbdraFilms-A7IV20260806_8223",
    "AbdraFilms-A7IV20260806_8224", "AbdraFilms-A7IV20260806_8226", "AbdraFilms-A7IV20260806_8227",
    "AbdraFilms-A7IV20260806_8233",
    # Sony A7S
    "AbdraFilms-A7s20260727_9107", "AbdraFilms-A7s20260804_9172", "AbdraFilms-A7s20260804_9173",
    "AbdraFilms-A7s20260804_9175", "AbdraFilms-A7s20260804_9176", "AbdraFilms-A7s20260804_9179",
    "AbdraFilms-A7s20260804_9198", "AbdraFilms-A7s20260804_9203", "AbdraFilms-A7s20260804_9209",
    "AbdraFilms-A7s20260804_9211", "AbdraFilms-A7s20260804_9212", "AbdraFilms-A7s20260804_9214",
    "AbdraFilms-A7s20260804_9216", "AbdraFilms-A7s20260804_9220", "AbdraFilms-A7s20260804_9230",
    "AbdraFilms-A7s20260804_9231", "AbdraFilms-A7s20260804_9235", "AbdraFilms-A7s20260804_9241",
    "AbdraFilms-A7s20260804_9259", "AbdraFilms-A7s20260804_9260", "AbdraFilms-A7s20260805_9291",
    "AbdraFilms-A7s20260805_9292", "AbdraFilms-A7s20260805_9295", "AbdraFilms-A7s20260805_9298",
    "AbdraFilms-A7s20260805_9300", "AbdraFilms-A7s20260805_9301", "AbdraFilms-A7s20260805_9313",
    "AbdraFilms-A7s20260805_9317", "AbdraFilms-A7s20260805_9318", "AbdraFilms-A7s20260805_9320",
    "AbdraFilms-A7s20260805_9326", "AbdraFilms-A7s20260805_9327", "AbdraFilms-A7s20260805_9333",
    "AbdraFilms-A7s20260806_9368", "AbdraFilms-A7s20260806_9372", "AbdraFilms-A7s20260806_9376",
    "AbdraFilms-A7s20260806_9377", "AbdraFilms-A7s20260806_9378", "AbdraFilms-A7s20260806_9382",
    "AbdraFilms-A7s20260806_9390", "AbdraFilms-A7s20260820_0006", "AbdraFilms-A7s20260820_0008",
    "AbdraFilms-A7s20260820_0014", "AbdraFilms-A7s20260820_0021",
    # DJI
    "DJI_20260727191357_0011_D_ABD", "DJI_20260727191804_0018_D_ABD", "DJI_20260804132644_0024_D_ABD",
    "DJI_20260804214749_0024_D_ABDRAFILMS", "DJI_20260805125817_0068_D_ABDRAFILMS",
    "DJI_20260806095235_0001_D_ABD", "DJI_20260806104427_0004_D_ABD", "DJI_20260806105138_0005_D_ABD",
    "DJI_20260806153417_0013_D_ABDRAFILMS", "DJI_20260820135006_0011_D_ABD", "DJI_20260820135737_0013_D_ABD",
    "DJI_20260820140232_0014_D_ABD", "DJI_20260820142651_0001_D", "DJI_20260820143132_0004_D",
    "DJI_20260820150311_0005_D", "DJI_20260820151353_0009_D", "DJI_20260820151712_0011_D",
    "DJI_20260820170229_0013_D", "DJI_20260820170404_0014_D", "DJI_20260820170727_0016_D",
    "DJI_20260820171112_0017_D", "DJI_20260820171439_0038_D"
]

# Build index of all files in F:\Arrow
print("Indexing F:\\Arrow...")
arrow_files = {}
for root, dirs, files in os.walk(r'F:\Arrow'):
    for f in files:
        base = os.path.splitext(f)[0]
        ext = os.path.splitext(f)[1].lower()
        if base not in arrow_files:
            arrow_files[base] = []
        arrow_files[base].append(os.path.join(root, f))

print(f"Indexed {len(arrow_files)} base names in F:\\Arrow.")

results = []

for clip in timeline_clips:
    # Look for matching files
    matches = arrow_files.get(clip, [])
    # Also check without trailing M01 if needed
    xml_path = None
    media_path = None
    
    # Check for direct or M01 XML
    for m in matches:
        if m.lower().endswith('.xml'):
            xml_path = m
        elif m.lower().endswith(('.mp4', '.mov')):
            if 'proxy' not in m.lower():
                media_path = m
            elif media_path is None:
                media_path = m
                
    # If no XML found directly, check if clip + "M01" exists
    if not xml_path:
        m01_matches = arrow_files.get(clip + "M01", [])
        for m in m01_matches:
            if m.lower().endswith('.xml'):
                xml_path = m
                
    # If still no media path, check matches
    if not media_path and matches:
        media_path = matches[0]

    gamma = "Unknown"
    primaries = "Unknown"
    camera_model = "Unknown"
    
    # Parse XML if available
    if xml_path and os.path.exists(xml_path):
        try:
            with open(xml_path, 'r', encoding='utf-8', errors='ignore') as xf:
                xml_text = xf.read()
                dev_match = re.search(r'modelName="([^"]+)"', xml_text)
                if dev_match: camera_model = dev_match.group(1)
                
                gamma_m = re.search(r'name="CaptureGammaEquation"\s+value="([^"]+)"', xml_text)
                if gamma_m: gamma = gamma_m.group(1)
                
                prim_m = re.search(r'name="CaptureColorPrimaries"\s+value="([^"]+)"', xml_text)
                if prim_m: primaries = prim_m.group(1)
        except Exception as e:
            gamma = f"XML Error: {e}"
            
    # For DJI or clips without XML, use ffprobe
    dji_profile = "N/A"
    if "dji" in clip.lower() or (media_path and "dji" in media_path.lower()):
        camera_model = "DJI Drone"
        if media_path and os.path.exists(media_path):
            try:
                cmd = [
                    r'C:\Program Files\FFmpeg\bin\ffprobe.exe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_streams',
                    '-show_format',
                    media_path
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                info = json.loads(proc.stdout)
                vid_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), {})
                c_space = vid_stream.get('color_space', '')
                c_transfer = vid_stream.get('color_transfer', '')
                c_primaries = vid_stream.get('color_primaries', '')
                pix_fmt = vid_stream.get('pix_fmt', '')
                
                tags = vid_stream.get('tags', {})
                format_tags = info.get('format', {}).get('tags', {})
                
                dji_profile = f"{c_space}/{c_transfer}/{c_primaries} ({pix_fmt})"
                # Check for D-Log / D-Cinelike in tags
                all_tags_str = str(tags) + str(format_tags)
                if "D-Log" in all_tags_str or "dlog" in all_tags_str.lower():
                    gamma = "D-Log"
                elif "D-Cinelike" in all_tags_str or "cinelike" in all_tags_str.lower():
                    gamma = "D-Cinelike"
                else:
                    gamma = f"DJI ({c_transfer or 'rec709'})"
                primaries = c_primaries or "bt709"
            except Exception as e:
                dji_profile = f"ffprobe error: {e}"

    results.append({
        'clip': clip,
        'camera': camera_model,
        'gamma': gamma,
        'primaries': primaries,
        'has_xml': bool(xml_path),
        'xml_path': xml_path,
        'media_path': media_path,
        'dji_info': dji_profile
    })

print(f"\nAnalyzed {len(results)} timeline clips:")
for r in results:
    print(f"[{r['clip']}] -> Camera: {r['camera']} | Gamma: {r['gamma']} | Primaries: {r['primaries']} | Has XML: {r['has_xml']}")

with open(r'c:\Users\Mi5a\VegasDavinciLinkTool\scratch\timeline_color_audit.json', 'w', encoding='utf-8') as out_f:
    json.dump(results, out_f, indent=2)
