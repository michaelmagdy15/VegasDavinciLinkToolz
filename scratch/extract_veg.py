import re
import os
import sys

veg_file = r'G:\Promo Arrow FinalCUTS3.0.veg'
print(f"Reading {veg_file}...")
with open(veg_file, 'rb') as f:
    raw = f.read()

print(f"Total size: {len(raw)} bytes")

# Search for paths
pattern_ascii = re.findall(rb'[FfEeCcDd]:\\[^\x00-\x1f\x7f\r\n\t<>\"|?*]+?\.(?:mp4|MP4|mov|MOV|m4v|M4V|avi|wav|mp3)', raw)
pattern_utf16 = re.findall(rb'(?:[FfEeCcDd]\x00:\x00\\\x00[^\x00\r\n\t<>\"|?*]+?\x00\.\x00(?:m\x00p\x004\x00|M\x00P\x004\x00|m\x00o\x00v\x00|M\x00O\x00V\x00|w\x00a\x00v\x00|m\x00p\x003\x00))', raw)

found = set()
for p in pattern_ascii:
    try:
        s = p.decode('utf-8', errors='ignore')
        if os.path.exists(s):
            found.add(s)
    except:
        pass

for p in pattern_utf16:
    try:
        s = p.decode('utf-16le', errors='ignore')
        if os.path.exists(s):
            found.add(s)
    except:
        pass

print(f"Found {len(found)} existing media files referenced in VEG:")
video_files = [f for f in found if f.lower().endswith(('.mp4', '.mov'))]
print(f"Video files: {len(video_files)}")
for f in sorted(video_files)[:30]:
    print("  ", f)
