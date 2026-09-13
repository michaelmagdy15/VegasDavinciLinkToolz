import sys
sys.path.insert(0, r"c:\Users\Mi5a\VegasDavinciLinkTool")
from core.live_bridge import load_manifest_json

ds = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')

print(f"=== DEEP SCAN: {ds.get('project_path', 'unknown')} ===")
print(f"Resolution: {ds.get('width')}x{ds.get('height')} @ {ds.get('frame_rate')} fps")
print(f"Total tracks: {len(ds.get('tracks', []))}")

tracks = ds.get('tracks', [])
for t in tracks:
    idx = t.get('index')
    name = t.get('name', '')
    mtype = t.get('type', '')
    vol = t.get('volume_db', t.get('volume', 0.0))
    comp_lvl = t.get('composite_level', 1.0)
    comp_mode = t.get('composite_mode', 'Normal')
    fx_list = [f.get('name') for f in t.get('effects', t.get('fx', []))]
    events = t.get('events', [])
    
    is_interesting = (
        (mtype == 'Audio' and (vol != 0.0 or len(fx_list) > 0)) or
        (mtype == 'Video' and (comp_lvl != 1.0 or comp_mode not in ('Normal', 'SourceAlpha', None))) or
        'burn' in name.lower() or
        len(events) > 0
    )
    if is_interesting:
        print(f"Track #{idx} [{mtype}] '{name}': {len(events)} events | vol_db={vol} | comp_lvl={comp_lvl} | comp_mode={comp_mode} | fx={fx_list}")

print("\n=== CLIPS WITH FADES / CROSSFADES ===")
fade_count = 0
for t in tracks:
    for ev in t.get('events', []):
        fin = ev.get('fade_in_ms', ev.get('fadeIn', 0))
        fout = ev.get('fade_out_ms', ev.get('fadeOut', 0))
        fin_curve = ev.get('fade_in_curve', ev.get('fadeInCurve', ''))
        fout_curve = ev.get('fade_out_curve', ev.get('fadeOutCurve', ''))
        if fin > 0 or fout > 0:
            fade_count += 1
            print(f"Track {t.get('index')} ({t.get('type')}) Event '{ev.get('name', ev.get('active_take', ''))}': In={fin}ms ({fin_curve}), Out={fout}ms ({fout_curve}), Start={ev.get('start_ms', ev.get('start'))}ms, Dur={ev.get('length_ms', ev.get('length'))}ms")
print(f"Total events with fades in deep scan: {fade_count}")

print("\n=== FILM BURN CLIPS SPECIFICS ===")
for t in tracks:
    for ev in t.get('events', []):
        name = ev.get('name', '') or ''
        take = ev.get('active_take', '') or ''
        fp = ev.get('file_path', '') or ''
        if 'burn' in name.lower() or 'burn' in take.lower() or 'burn' in fp.lower() or 'burn' in t.get('name', '').lower():
            print(f"FilmBurn Clip: '{name or take}' on Track #{t.get('index')} ({t.get('name')})")
            print(f"   file: {fp}")
            print(f"   crop: {ev.get('crop')}")
            print(f"   pan: {ev.get('pan')}")
            print(f"   track composite_mode: {t.get('composite_mode')}")
            print(f"   track composite_level: {t.get('composite_level')}")
            print(f"   track motion: {t.get('track_motion')}")
            print(f"   event opacity: {ev.get('opacity', ev.get('take_gain', 1.0))}")
