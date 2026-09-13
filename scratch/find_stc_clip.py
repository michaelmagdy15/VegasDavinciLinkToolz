import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

print("Searching for clip with source timecode 00:05:43:05...")
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        stc = it.GetSourceStartTime()
        etc = it.GetSourceEndTime()
        if stc or etc:
            # check if 00:05:43 is in range
            if "00:05:4" in str(stc) or "00:05:4" in str(etc):
                print(f"Match V{v}: {it.GetName()} | SourceStart: {stc} | SourceEnd: {etc} | Comps: {it.GetFusionCompCount()}")
