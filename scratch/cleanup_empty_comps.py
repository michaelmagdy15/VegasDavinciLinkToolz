import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

cleaned = 0
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        cnt = it.GetFusionCompCount()
        if cnt > 0:
            names = list(it.GetFusionCompNameList())
            for cname in names:
                comp = it.GetFusionCompByName(cname)
                if not comp: continue
                tools = comp.GetToolList()
                tnames = set(t.GetAttrs().get('TOOLS_RegID', '') for t in tools.values())
                # If only MediaIn and MediaOut (or empty)
                if tnames.issubset({'MediaIn', 'MediaOut'}):
                    print(f"Removing empty passthrough comp '{cname}' from V{v} '{it.GetName()}'...")
                    it.DeleteFusionCompByName(cname)
                    cleaned += 1

print(f"\nCleaned up {cleaned} redundant Fusion comps!")
