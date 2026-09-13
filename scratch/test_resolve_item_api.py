import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

# Test Video Item
vitems = tl.GetItemListInTrack("video", 24) or []
if vitems:
    vitem = vitems[0]
    print(f"Video Item: {vitem.GetName()}")
    print("Methods on TimelineItem:")
    for m in dir(vitem):
        if not m.startswith("_"):
            print(f"  {m}")
    print("\nGetting all properties with empty GetProperty():")
    try:
        props = vitem.GetProperty()
        print("Video Item Props:", props)
    except Exception as e:
        print("GetProperty() error:", e)

# Test Audio Item
aitems = tl.GetItemListInTrack("audio", 2) or []
if aitems:
    aitem = aitems[0]
    print(f"\nAudio Item: {aitem.GetName()}")
    try:
        props = aitem.GetProperty()
        print("Audio Item Props:", props)
    except Exception as e:
        print("Audio GetProperty() error:", e)
