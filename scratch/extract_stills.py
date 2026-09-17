import os, subprocess
from core.live_bridge import load_manifest_json

d = load_manifest_json(r'C:\Users\Mi5a\.timeline_bridge\vegas_deep_scan.json')
out_dir = r'c:\Users\Mi5a\VegasDavinciLinkTool\scratch\stills'
os.makedirs(out_dir, exist_ok=True)

# List of replacements with original and new files and offsets
shots = [
    {
        "id": 1,
        "time": "13.7s",
        "orig_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9209.MP4",
        "orig_offset_s": 0.0,
        "new_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna brolls\AbdraFilms-A7s20260804_9198.MP4",
        "new_offset_s": 0.0,
        "label": "Shot 1 (13.7s) - Kite Pumping"
    },
    {
        "id": 2,
        "time": "26.4s",
        "orig_file": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820170229_0013_D.MP4",
        "orig_offset_s": 2.0,
        "new_file": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820170404_0014_D.MP4",
        "new_offset_s": 2.0,
        "label": "Shot 2 (26.4s) - Drone Golden Hour"
    },
    {
        "id": 3,
        "time": "32.8s",
        "orig_file": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\drone sokhna" + chr(0xf028) + r"\DJI_20260805125817_0068_D_ABDRAFILMS.MP4",
        "orig_offset_s": 0.0,
        "new_file": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820142651_0001_D.MP4",
        "new_offset_s": 13.96,
        "label": "Shot 3 (32.8s) - Blue Lagoon Drone"
    },
    {
        "id": 4,
        "time": "33.8s",
        "orig_file": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820143132_0004_D.MP4",
        "orig_offset_s": 0.0,
        "new_file": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820171112_0017_D.MP4",
        "new_offset_s": 1.5,
        "label": "Shot 4 (33.8s) - Low Water Chase"
    },
    {
        "id": 5,
        "time": "41.3s",
        "orig_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9212.MP4",
        "orig_offset_s": 0.0,
        "new_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\kiting hurghada\AbdraFilms-A7IV20260806_8226.MP4",
        "new_offset_s": 1.0,
        "label": "Shot 5 (41.3s) - Aerial Board Off"
    },
    {
        "id": 6,
        "time": "43.8s",
        "orig_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9231.MP4",
        "orig_offset_s": 0.0,
        "new_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9230.MP4",
        "new_offset_s": 1.5,
        "label": "Shot 6 (43.8s) - Landed Kiteloop"
    },
    {
        "id": 7,
        "time": "47.4s",
        "orig_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260806_9382.MP4",
        "orig_offset_s": 0.0,
        "new_file": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9214.MP4",
        "new_offset_s": 2.0,
        "label": "Shot 7 (47.4s) - Water Spray at Lens"
    }
]

for s in shots:
    # Extract new frame
    new_out = os.path.join(out_dir, f"shot_{s['id']}_new.jpg")
    if os.path.exists(s["new_file"]):
        cmd = ["ffmpeg", "-y", "-ss", str(s["new_offset_s"]), "-i", s["new_file"], "-vframes", "1", "-q:v", "3", new_out]
        subprocess.run(cmd, capture_output=True)
        print(f"Extracted Shot {s['id']} New: {new_out} exists={os.path.exists(new_out)}")
    else:
        print(f"New file not found: {s['new_file']}")
