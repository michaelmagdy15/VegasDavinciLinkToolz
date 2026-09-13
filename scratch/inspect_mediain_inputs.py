import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

# Inspect V18 clip at frame 86632
v18_items = tl.GetItemListInTrack('video', 18) or []
for it in v18_items:
    if it.GetStart() <= 86632 < it.GetEnd():
        print(f"Clip: {it.GetName()}")
        comp = it.GetFusionCompByIndex(1)
        tools = comp.GetToolList()
        mi = next((t for t in tools.values() if 'MediaIn' in t.GetAttrs().get('TOOLS_Name', '')), None)
        if mi:
            print("MediaIn inputs:")
            inps = mi.GetInputList()
            for k, inp in inps.items():
                attrs = inp.GetAttrs()
                name = attrs.get('INPS_Name')
                iid = attrs.get('INPS_ID')
                if any(x in name.lower() for x in ['hold', 'extend', 'post', 'pre', 'loop', 'time', 'layer', 'clip', 'frame', 'trim']):
                    print(f"  {name} (ID: {iid}) = {mi.GetInput(iid)}")
