import sys
import os

sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
items = tl.GetItemListInTrack("video", 2)
if items:
    it = items[0]
    print("Initial CompositeMode:", it.GetProperty("CompositeMode"))
    for val in range(25):
        ok = it.SetProperty("CompositeMode", val)
        got = it.GetProperty("CompositeMode")
        if ok and got == val:
            print(f"CompositeMode {val} is valid")
        else:
            break
            
    print("\nTesting Scaling property:")
    print("Initial Scaling:", it.GetProperty("Scaling"))
    for val in range(10):
        ok = it.SetProperty("Scaling", val)
        got = it.GetProperty("Scaling")
        if ok and got == val:
            print(f"Scaling {val} is valid")
        else:
            break

    # Reset CompositeMode to 0
    it.SetProperty("CompositeMode", 0)
    it.SetProperty("Scaling", 0)
