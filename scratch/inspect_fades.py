import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"c:\Users\Mi5a\VegasDavinciLinkTool")
from core.live_bridge import load_manifest_json

tl = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')

print("=== CLIPS WITH FADES IN VEGAS_TIMELINE.JSON ===")
count = 0
for t in tl.get('tracks', []):
    t_idx = t.get('index')
    t_name = t.get('name')
    is_vid = t.get('is_video')
    for c in t.get('clips', []):
        fin = c.get('fade_in_ms', 0)
        fout = c.get('fade_out_ms', 0)
        fin_c = c.get('fade_in_curve', '')
        fout_c = c.get('fade_out_curve', '')
        if fin > 0 or fout > 0:
            count += 1
            print(f"[{'V' if is_vid else 'A'}{t_idx}] '{c.get('name')}': start={c.get('timeline_start_ms')}ms, len={c.get('timeline_length_ms')}ms | In={fin}ms ({fin_c}), Out={fout}ms ({fout_c})")
print(f"Total clips with fades: {count}")
