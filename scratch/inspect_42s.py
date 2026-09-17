import json

with open(r'c:\Users\Mi5a\VegasDavinciLinkTool\vegas_timeline.json') as f:
    tl = json.load(f)

print("--- MARKERS ---")
for m in tl.get('markers', []):
    name = m.get('name', '')
    pos = m.get('position_ms', 0)
    if '10' in name or '11' in name or (40000 <= pos <= 45000):
        print(f"Marker '{name}' at {pos}ms ({pos/1000.0:.2f}s)")

print("\n--- EVENTS AROUND 41-45s ---")
for trk in tl.get('tracks', []):
    for ev in trk.get('events', []):
        t_start = ev.get('start_time_ms', 0)
        t_len = ev.get('length_ms', 0)
        if 40000 <= t_start <= 46000:
            at = ev.get('active_take') or {}
            print(f"Track '{trk.get('name')}' (idx {trk.get('index')}):")
            print(f"  Event: '{ev.get('name')}', Start: {t_start}ms, Length: {t_len}ms")
            print(f"  Take: '{at.get('name')}'")
            print(f"  Media: {at.get('media_path')}")
            print(f"  Offset: {at.get('offset_ms')}ms")
