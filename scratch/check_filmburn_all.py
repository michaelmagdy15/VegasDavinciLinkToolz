import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr
tl = dvr.scriptapp('Resolve').GetProjectManager().GetCurrentProject().GetCurrentTimeline()

print(f"Active Timeline: {tl.GetName()}")
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        name = it.GetName().lower()
        tname = tl.GetTrackName("video", v).lower()
        if 'burn' in name or 'burn' in tname:
            print(f"V{v} ({tl.GetTrackName('video', v)}): {it.GetName()}")
            print(f"   CompMode: {it.GetProperty('CompositeMode')}")
            print(f"   Opacity:  {it.GetProperty('Opacity')}")
            print(f"   Zoom:     ({it.GetProperty('ZoomX')}, {it.GetProperty('ZoomY')})")
            print(f"   Pan/Tilt: ({it.GetProperty('Pan')}, {it.GetProperty('Tilt')})")
            print(f"   Scaling:  {it.GetProperty('Scaling')}")
