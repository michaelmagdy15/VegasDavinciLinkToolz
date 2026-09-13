import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr
tl = dvr.scriptapp('Resolve').GetProjectManager().GetCurrentProject().GetCurrentTimeline()

aitem = tl.GetItemListInTrack('audio', 2)[0]
print(f"Testing properties on audio item: '{aitem.GetName()}'")

test_keys = [
    "Volume", "volume", "Gain", "gain", "AudioGain", "audioGain", "Level", "level",
    "ClipGain", "Pan", "pan", "AudioPan", "FadeIn", "FadeOut", "ClipColor"
]

for k in test_keys:
    val = aitem.GetProperty(k)
    if val is not None:
        print(f"  Found readable property: {k} = {val}")

# Test if SetProperty works or raises error
for k in ["ClipGain", "Volume", "AudioGain", "Pan"]:
    try:
        ok = aitem.SetProperty(k, 1.0)
        print(f"  SetProperty({k}, 1.0) -> {ok} | Readback: {aitem.GetProperty(k)}")
    except Exception as e:
        print(f"  SetProperty({k}) error: {e}")
