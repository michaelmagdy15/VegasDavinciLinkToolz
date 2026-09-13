import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr
tl = dvr.scriptapp('Resolve').GetProjectManager().GetCurrentProject().GetCurrentTimeline()

print(f"Timeline: {tl.GetName()}")
for v in range(1, tl.GetTrackCount('video') + 1):
    tname = tl.GetTrackName('video', v)
    items = tl.GetItemListInTrack('video', v) or []
    if items:
        opacities = set(round(it.GetProperty('Opacity'), 2) for it in items)
        comp_modes = set(it.GetProperty('CompositeMode') for it in items)
        print(f"V{v:02d} '{tname}' ({len(items):02d} items) -> Opacity: {opacities} | CompMode: {comp_modes}")
