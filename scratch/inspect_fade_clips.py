import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
vitem = tl.GetItemListInTrack('video', 24)[0]
print("vitem:", vitem.GetName())
print("FusionCompCount:", vitem.GetFusionCompCount())
print("FusionCompNames:", vitem.GetFusionCompNameList())

# If we check an item that has fades, e.g. V16 or V22:
# Let's find AbdraFilms-A7IV20260805_8156 or AbdraFilms-A7IV20260804_8123
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        if "8156" in it.GetName() or "8123" in it.GetName():
            print(f"Found clip with fade on V{v}: {it.GetName()} | Dur={it.GetDuration()} | Start={it.GetStart()} | End={it.GetEnd()}")
