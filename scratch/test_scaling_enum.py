import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr
tl = dvr.scriptapp('Resolve').GetProjectManager().GetCurrentProject().GetCurrentTimeline()
item = tl.GetItemListInTrack('video', 24)[0]

print("Current Scaling:", item.GetProperty("Scaling"))
print("Current Zoom:", item.GetProperty("ZoomX"), item.GetProperty("ZoomY"))
# Let's inspect the media pool clip for filmburn_6.mov
mp_item = item.GetMediaPoolItem()
if mp_item:
    print("MediaPoolItem Clip Properties:")
    cp = mp_item.GetClipProperty()
    for k in ["Resolution", "FPS", "Aspect Ratio", "Input Sizing Preset", "Video Codec"]:
        print(f"  {k}: {cp.get(k)}")
