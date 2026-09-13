import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

print("=== AUDITING ALL CLIPS WITH FUSION COMPS IN TIMELINE ===")
faulty_clips = []
for v in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', v) or []
    for it in items:
        cnt = it.GetFusionCompCount()
        if cnt > 0:
            for cidx in range(1, cnt + 1):
                comp = it.GetFusionCompByIndex(cidx)
                if not comp: continue
                tools = comp.GetToolList()
                tnames = [t.GetAttrs().get('TOOLS_Name', '') for t in tools.values()]
                if 'TimeSpeed1' in tnames:
                    faulty_clips.append((v, it, comp))
                    print(f"V{v:02d} '{it.GetName()}' [Dur: {it.GetDuration()}]: Comp {cidx} has TimeSpeed1! Tools: {tnames}")

print(f"\nTotal clips with TimeSpeed1 comps: {len(faulty_clips)}")
