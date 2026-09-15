import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import os

with open(r'G:\Promo Arrow FinalCUTS3.0.veg', 'rb') as f:
    raw = f.read()

# Extract all UTF-16LE strings of length >= 4
all_utf16_bytes = re.findall(rb'(?:[\x20-\x7e]\x00){4,}', raw)
all_strings = [b.decode('utf-16le', errors='ignore') for b in all_utf16_bytes]

print(f"Total UTF-16 strings extracted: {len(all_strings)}")

# Separate into media paths, take names, track names, etc.
media_files = set()
event_names = set()

for s in all_strings:
    s_strip = s.strip()
    if any(s_strip.lower().endswith(ext) for ext in ['.mp4', '.mov', '.m4v']):
        media_files.add(s_strip)
    elif any(k in s_strip for k in ['AbdraFilms', 'DJI_', 'filmburn', 'LIGHT_']):
        event_names.add(s_strip)

print(f"Media files ({len(media_files)}):")
for m in sorted(list(media_files))[:20]:
    print("  M:", m)

print(f"\nEvent takes ({len(event_names)}):")
for e in sorted(list(event_names))[:30]:
    print("  E:", e)
