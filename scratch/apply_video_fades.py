import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

def apply_video_fade(item, fade_in_ms=0, fade_out_ms=0, fps=24.0):
    dur = item.GetDuration()
    if dur <= 1 or (fade_in_ms <= 0 and fade_out_ms <= 0):
        return
    
    # Check if comp already exists
    if item.GetFusionCompCount() > 0:
        comp = item.GetFusionCompByIndex(1)
    else:
        comp = item.AddFusionComp()
    
    if not comp:
        return
    
    tools = comp.GetToolList()
    media_in = None
    media_out = None
    bc = None
    for t in tools.values():
        tname = t.GetAttrs().get('TOOLS_Name', '')
        if 'MediaIn' in tname: media_in = t
        elif 'MediaOut' in tname: media_out = t
        elif 'BrightnessContrast' in tname: bc = t
    
    if not media_in or not media_out:
        return
    
    if not bc:
        bc = comp.AddTool("BrightnessContrast")
        bc.ConnectInput("Input", media_in)
        media_out.ConnectInput("Input", bc)
    
    gain = bc.Gain
    if fade_in_ms > 0:
        fin_frames = max(1, int(round((fade_in_ms / 1000.0) * fps)))
        fin_frames = min(dur - 1, fin_frames)
        gain[0] = 0.0
        gain[fin_frames] = 1.0
        print(f"  Applied Fade-In on {item.GetName()}: 0 to {fin_frames} frames ({fade_in_ms:.1f}ms)")
    
    if fade_out_ms > 0:
        fout_frames = max(1, int(round((fade_out_ms / 1000.0) * fps)))
        fout_frames = min(dur - 1, fout_frames)
        start_f = max(0, dur - fout_frames)
        gain[start_f] = 1.0
        gain[dur - 1] = 0.0
        print(f"  Applied Fade-Out on {item.GetName()}: {start_f} to {dur - 1} frames ({fade_out_ms:.1f}ms)")

# Apply to V12 and V6
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        if "8156" in it.GetName() and it.GetStart() == 86400: # V12 event at start=0 (timeline start frame 86400)
            apply_video_fade(it, fade_out_ms=66.73)
        elif "8123" in it.GetName():
            apply_video_fade(it, fade_out_ms=834.17)
