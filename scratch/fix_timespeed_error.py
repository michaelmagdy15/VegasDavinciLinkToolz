import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

# Fix all clips that have TimeSpeed1
fixed = 0
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        cnt = it.GetFusionCompCount()
        if cnt > 0:
            for cidx in range(1, cnt + 1):
                comp = it.GetFusionCompByIndex(cidx)
                if not comp: continue
                tools = comp.GetToolList()
                ts = next((t for t in tools.values() if 'TimeSpeed' in t.GetAttrs().get('TOOLS_Name', '')), None)
                if ts:
                    mi = next((t for t in tools.values() if 'MediaIn' in t.GetAttrs().get('TOOLS_Name', '')), None)
                    mo = next((t for t in tools.values() if 'MediaOut' in t.GetAttrs().get('TOOLS_Name', '')), None)
                    if mo and mi:
                        print(f"Bypassing TimeSpeed1 on V{v} '{it.GetName()}'...")
                        mo.ConnectInput("Input", mi)
                        ts.Delete()
                        fixed += 1

print(f"\nSuccessfully removed TimeSpeed1 from {fixed} clips!")
