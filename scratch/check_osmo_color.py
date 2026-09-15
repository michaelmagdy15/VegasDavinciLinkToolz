import subprocess, json

files = [
    (r'F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\DJI_20260727191357_0011_D_ABD.mp4', 'OsmoAction5 Pro'),
    (r'F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\DJI_20260804214749_0024_D_ABDRAFILMS.MP4', 'Air3s'),
    (r'F:\Arrow\arrow kite surf 2\sorted 2\drone\dahab blue lagoon\DJI_20260820142651_0001_D.MP4', 'Mini4 Pro')
]

for p, label in files:
    cmd = [r'C:\Program Files\FFmpeg\bin\ffprobe.exe', '-v', 'quiet', '-show_streams', '-print_format', 'json', p]
    res = subprocess.run(cmd, capture_output=True, text=True)
    j = json.loads(res.stdout)
    v = next(s for s in j.get('streams', []) if s.get('codec_type') == 'video')
    print(label + ": " + str(v.get('pix_fmt')) + " | " + str(v.get('color_space')) + " | " + str(v.get('color_transfer')))
