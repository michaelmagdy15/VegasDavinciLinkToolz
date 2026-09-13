import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr
tl = dvr.scriptapp('Resolve').GetProjectManager().GetCurrentProject().GetCurrentTimeline()

print(f"Timeline: {tl.GetName()}")
for a in range(1, tl.GetTrackCount('audio') + 1):
    tname = tl.GetTrackName('audio', a)
    items = tl.GetItemListInTrack('audio', a) or []
    cnames = [it.GetName() for it in items[:3]]
    print(f"Resolve A{a:02d} '{tname}' ({len(items)} items): {cnames}")
