import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

# Let's find AbdraFilms-A7IV20260804_8123 on V6
items = tl.GetItemListInTrack('video', 6) or []
target = None
for it in items:
    if "8123" in it.GetName():
        target = it
        break

if target:
    print(f"Target clip: {target.GetName()} (Dur: {target.GetDuration()})")
    comp = target.AddFusionComp()
    if comp:
        print("Created Fusion Comp:", comp.GetAttrs()['COMPS_Name'])
        tools = comp.GetToolList()
        # Find MediaIn and MediaOut
        media_in = None
        media_out = None
        for t in tools.values():
            tname = t.GetAttrs().get('TOOLS_Name', '')
            if 'MediaIn' in tname: media_in = t
            if 'MediaOut' in tname: media_out = t
        print(f"MediaIn: {media_in}, MediaOut: {media_out}")
        if media_in and media_out:
            bc = comp.AddTool("BrightnessContrast")
            if bc:
                print("Added BrightnessContrast:", bc.GetAttrs()['TOOLS_Name'])
                # Connect MediaIn -> BrightnessContrast -> MediaOut
                bc.ConnectInput("Input", media_in)
                media_out.ConnectInput("Input", bc)
                # Keyframe Gain
                dur = target.GetDuration()
                fade_frames = min(dur - 1, int(round(24.0 * 0.834)))  # 834 ms at 24fps = 20 frames
                start_fade = max(0, dur - fade_frames)
                gain = bc.Gain
                gain[start_fade] = 1.0
                gain[dur - 1] = 0.0
                print(f"Keyframed fade out: frame {start_fade} (1.0) -> frame {dur - 1} (0.0)")
