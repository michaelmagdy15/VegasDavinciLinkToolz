import os, subprocess

files = {
    "9198": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna brolls\AbdraFilms-A7s20260804_9198.MP4",
    "0014_D": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820170404_0014_D.MP4",
    "0016_D": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820170817_0016_D.MP4",
    "0001_D": r"F:\Arrow\arrow kite surf 2\sorted 2\drone" + chr(0xf028) + r"\dahab blue lagoon\DJI_20260820142651_0001_D.MP4",
    "8226": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\kiting hurghada\AbdraFilms-A7IV20260806_8226.MP4",
    "9230": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9230.MP4",
    "9214": r"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9214.MP4",
}

for name, path in files.items():
    if not os.path.exists(path):
        print(f"File {name} does not exist")
        continue
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    dur = float(subprocess.check_output(cmd).decode().strip())
    print(f"{name}: duration = {dur:.2f}s ({dur/60:.1f} min)")
