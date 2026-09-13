import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

for v in [12, 18, 6]:
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        if it.GetFusionCompCount() > 0:
            print(f"\n==================================================")
            print(f"Checking V{v} clip '{it.GetName()}' [Dur: {it.GetDuration()}]")
            for cidx in range(1, it.GetFusionCompCount() + 1):
                comp = it.GetFusionCompByIndex(cidx)
                attrs = comp.GetAttrs()
                print(f"Comp {cidx}: RenderStart={attrs.get('COMPN_RenderStartTime')}, RenderEnd={attrs.get('COMPN_RenderEndTime')}, GlobalStart={attrs.get('COMPN_GlobalStartTime')}, GlobalEnd={attrs.get('COMPN_GlobalEndTime')}")
                for tid, tool in comp.GetToolList().items():
                    tname = tool.GetAttrs().get('TOOLS_Name')
                    treg = tool.GetAttrs().get('TOOLS_RegID')
                    print(f"  Tool {tname} ({treg}):")
                    # Check MediaIn / MediaOut
                    if 'MediaIn' in tname:
                        for attr_name in ['INP_HoldFirstFrame', 'INP_HoldLastFrame', 'MediaProps']:
                            val = tool.GetInput(attr_name)
                            if val is not None:
                                print(f"     {attr_name}: {val}")
                        # Check inputs
                        for inp in tool.GetInputs().values():
                            in_attrs = inp.GetAttrs()
                            iname = in_attrs.get('INPS_Name')
                            if iname in ['Hold First Frame', 'Hold Last Frame', 'Source Track', 'Global In', 'Global Out']:
                                print(f"     {iname}: {tool.GetInput(in_attrs.get('INPS_ID'))}")
                    elif 'TimeSpeed' in tname:
                        ts_speed = tool.GetInput("Speed")
                        print(f"     Speed: {ts_speed}")
                    elif 'BrightnessContrast' in tname:
                        gain = tool.GetInput("Gain")
                        print(f"     Gain: {gain}")
