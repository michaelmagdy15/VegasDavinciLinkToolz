import sys
sys.path.insert(0, r"c:\Users\Mi5a\VegasDavinciLinkTool")
from core.live_bridge import load_manifest_json

tl = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_timeline.json')

print(f"=== PROJECT: {tl.get('project_path', 'unknown')} ===")
print(f"Resolution: {tl.get('width')}x{tl.get('height')} @ {tl.get('frame_rate')} fps")
print(f"Total tracks: {len(tl.get('tracks', []))}")

tracks = tl.get('tracks', [])
for t in tracks:
    idx = t.get('index')
    name = t.get('name', '')
    mtype = t.get('type', '')
    vol = t.get('volume_db', t.get('volume', 0.0))
    comp_lvl = t.get('composite_level', 1.0)
    comp_mode = t.get('composite_mode', 'Normal')
    fx_list = [f.get('name') for f in t.get('fx', [])]
    events = t.get('events', [])
    
    # Check if anything interesting
    is_interesting = (
        (mtype == 'Audio' and vol != 0.0) or
        (mtype == 'Video' and comp_lvl != 1.0) or
        (mtype == 'Video' and comp_mode not in ('Normal', 'SourceAlpha', None)) or
        len(fx_list) > 0 or
        'burn' in name.lower()
    )
    if is_interesting:
        print(f"Track #{idx} [{mtype}] '{name}': {len(events)} events | vol_db={vol} | comp_lvl={comp_lvl} | comp_mode={comp_mode} | fx={fx_list}")

print("\n=== CLIPS WITH FADES / CROSSFADES ===")
fade_count = 0
for t in tracks:
    for ev in t.get('events', []):
        fin = ev.get('fade_in_ms', 0)
        fout = ev.get('fade_out_ms', 0)
        fin_curve = ev.get('fade_in_curve', '')
        fout_curve = ev.get('fade_out_curve', '')
        if fin > 0 or fout > 0:
            fade_count += 1
            print(f"Track {t.get('index')} ({t.get('type')}) Event '{ev.get('name')}': In={fin}ms ({fin_curve}), Out={fout}ms ({fout_curve}), Start={ev.get('start_ms')}ms, Dur={ev.get('length_ms')}ms")
print(f"Total events with fades: {fade_count}")

print("\n=== FILM BURN CLIPS SPECIFICS ===")
for t in tracks:
    for ev in t.get('events', []):
        if 'burn' in ev.get('name', '').lower() or 'burn' in t.get('name', '').lower():
            print(f"FilmBurn Clip: '{ev.get('name')}' on Track #{t.get('index')}")
            print(f"   file: {ev.get('file_path')}")
            print(f"   crop: {ev.get('crop')}")
            print(f"   pan: {ev.get('pan')}")
            print(f"   track composite_mode: {t.get('composite_mode')}")
            print(f"   track composite_level: {t.get('composite_level')}")
            print(f"   track motion: {t.get('track_motion')}")
            print(f"   event opacity: {ev.get('opacity', ev.get('take_gain', 1.0))}")
