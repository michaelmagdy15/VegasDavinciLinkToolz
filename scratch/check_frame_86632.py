import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr
tl = dvr.scriptapp('Resolve').GetProjectManager().GetCurrentProject().GetCurrentTimeline()
f = 86400 + 9 * 24 + 16
print(f"Current Playhead Timecode: {tl.GetCurrentTimecode()} (Frame: {f})")
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        if it.GetStart() <= f < it.GetEnd():
            print(f"V{v:02d} ({tl.GetTrackName('video', v)}): '{it.GetName()}' [{it.GetStart()} - {it.GetEnd()}] | Comps: {it.GetFusionCompCount()}")
