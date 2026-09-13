import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
items = tl.GetItemListInTrack('video', 6)
it = items[0]
comp = it.AddFusionComp()
print("Tools in fresh FusionComp:")
tools = comp.GetToolList()
for k, v in tools.items():
    print(f"  {k}: {v.GetAttrs()['TOOLS_Name']} ({v.GetAttrs()['TOOLB_Visible']})")
    print(f"     Inputs: {[inp.GetAttrs()['INPS_Name'] for inp in v.GetInputs().values() if 'INPS_Name' in inp.GetAttrs()][:5]}")

# Clean up
it.DeleteFusionCompByName(comp.GetAttrs()['COMPS_Name'])
