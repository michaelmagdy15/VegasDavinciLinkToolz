import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

# Check all clips that are visible at frame 86400 (playhead at beginning)
print("=== CLIPS AT TIMELINE START (FRAME 86400) ===")
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        if it.GetStart() <= 86400 < it.GetEnd():
            print(f"V{v} ({tl.GetTrackName('video', v)}): '{it.GetName()}' | [{it.GetStart()} - {it.GetEnd()}] | Comps: {it.GetFusionCompCount()}")
            if it.GetFusionCompCount() > 0:
                for cidx in range(1, it.GetFusionCompCount() + 1):
                    comp = it.GetFusionCompByIndex(cidx)
                    cname = it.GetFusionCompNameList()[cidx - 1] if cidx - 1 < len(it.GetFusionCompNameList()) else "comp"
                    tools = comp.GetToolList()
                    tnames = [t.GetAttrs().get('TOOLS_Name') for t in tools.values()]
                    print(f"   Comp {cidx} ({cname}): tools = {tnames}")
