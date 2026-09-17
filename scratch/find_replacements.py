import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from pathlib import Path

targets = [
    'AbdraFilms-A7s20260804_9198',
    'DJI_20260820170404_0014_D',
    'DJI_20260820142651_0001_D',
    'DJI_20260820171112_0017_D',
    'AbdraFilms-A7IV20260806_8226',
    'AbdraFilms-A7s20260804_9230',
    'AbdraFilms-A7s20260804_9214'
]

matches = {}
for root, dirs, files in os.walk(r'F:\Arrow'):
    for f in files:
        fl = f.lower()
        if not fl.endswith(('.mp4', '.mov')): continue
        if 'proxy' in root.lower(): continue
        for t in targets:
            if t.lower() in fl:
                if t not in matches:
                    matches[t] = []
                matches[t].append(os.path.join(root, f))

for t in targets:
    found = matches.get(t, [])
    print(f"Target [{t}]: {len(found)} candidates")
    for p in found:
        print(f"   -> {p}")
