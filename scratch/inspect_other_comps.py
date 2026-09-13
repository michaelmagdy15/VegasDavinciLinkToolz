import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

for v in [5, 6, 12, 15, 16, 22]:
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        cnt = it.GetFusionCompCount()
        if cnt > 0:
            for cidx in range(1, cnt + 1):
                comp = it.GetFusionCompByIndex(cidx)
                if not comp: continue
                tools = [t.GetAttrs().get('TOOLS_Name') for t in comp.GetToolList().values()]
                print(f"V{v:02d} '{it.GetName()}': Comp {cidx} -> {tools}")
