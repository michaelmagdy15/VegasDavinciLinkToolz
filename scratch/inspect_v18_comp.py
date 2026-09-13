import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

# Get the V18 clip at playhead [86619 - 86636]
v18_items = tl.GetItemListInTrack('video', 18) or []
for it in v18_items:
    if it.GetStart() <= 86632 < it.GetEnd():
        print(f"Inspecting V18 clip: '{it.GetName()}'")
        comp = it.GetFusionCompByIndex(1)
        print("Comp attrs:", comp.GetAttrs())
        tools = comp.GetToolList()
        for tid, tool in tools.items():
            tname = tool.GetAttrs().get('TOOLS_Name')
            treg = tool.GetAttrs().get('TOOLS_RegID')
            print(f"  Tool: {tname} ({treg})")
            if tname == 'TimeSpeed1':
                print(f"     Speed: {tool.GetInput('Speed')}")
                print(f"     Interpolation: {tool.GetInput('InterpolationMode')}")
            elif tname == 'MediaIn1':
                print(f"     MediaIn Inputs:")
                for inp in tool.GetInputList().values():
                    in_id = inp.GetAttrs().get('INPS_ID')
                    if in_id in ['HoldFirstFrame', 'HoldLastFrame', 'SourceTrack', 'GlobalIn', 'GlobalOut', 'ClipTimeEnd']:
                        print(f"        {in_id}: {tool.GetInput(in_id)}")
