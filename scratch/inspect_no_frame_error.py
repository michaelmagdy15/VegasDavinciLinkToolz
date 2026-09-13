import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

print(f"Active Timeline: {tl.GetName()}")
print(f"Current Timecode: {tl.GetCurrentTimecode()}")

# Find all clips that have Fusion comps
print("\n=== CLIPS WITH FUSION COMPS ===")
comps_found = []
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        cnt = it.GetFusionCompCount()
        if cnt > 0:
            names = it.GetFusionCompNameList()
            print(f"V{v} ({tl.GetTrackName('video', v)}): '{it.GetName()}' | Start: {it.GetStart()} | End: {it.GetEnd()} | Dur: {it.GetDuration()} | Comps: {cnt} ({names})")
            comps_found.append((v, it))

# Timecode 00:05:43:05 at 24 fps:
# 5 mins = 300s. 300 + 43 = 343s. 343 * 24 + 5 = 8232 + 5 = 8237 frames offset from start!
# Let's check timeline start frame:
start_frame = tl.GetStartFrame()
print(f"Timeline Start Frame: {start_frame}")
tc = "00:05:43:05"
parts = tc.split(":")
h, m, s, f = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
target_f = start_frame + (h * 3600 + m * 60 + s) * 24 + f
print(f"Target Frame for {tc} approx: {target_f}")

print("\n=== CLIPS ACTIVE AT OR NEAR THIS TIMECODE ===")
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        if it.GetStart() <= target_f <= it.GetEnd():
            print(f"V{v}: '{it.GetName()}' [{it.GetStart()} - {it.GetEnd()}] (Comps: {it.GetFusionCompCount()})")
