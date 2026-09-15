import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import os

with open(r'G:\Promo Arrow FinalCUTS3.0.veg', 'rb') as f:
    raw = f.read()

print(f"Size of 3.0.veg: {len(raw)} bytes")

# In Sony Vegas .veg, track headers and event take names appear in UTF-16LE
# Let's search for patterns
# Take names usually match: AbdraFilms-A7..., DJI_..., filmburn..., LIGHT_...
regex_takes = rb'(?:A\x00b\x00d\x00r\x00a\x00F\x00i\x00l\x00m\x00s\x00|D\x00J\x00I\x00_|f\x00i\x00l\x00m\x00b\x00u\x00r\x00n\x00|L\x00I\x00G\x00H\x00T\x00_)(?:[^\x00\r\n\t]\x00)+'

matches = re.findall(regex_takes, raw)
take_names = set()
for m in matches:
    name = m.decode('utf-16le', errors='ignore')
    take_names.add(name)

print(f"Found {len(take_names)} unique take/clip names matching project patterns in 3.0.veg:")
for n in sorted(list(take_names)):
    print("  ", n)
