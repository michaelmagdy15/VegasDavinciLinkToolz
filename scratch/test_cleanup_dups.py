import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()
rf = mp.GetRootFolder()

vfolder = None
for f in rf.GetSubFolderList():
    if f.GetName() == "VEGAS Live Import":
        vfolder = f
        break

if vfolder:
    clips = vfolder.GetClipList()
    print("Total clips in VEGAS Live Import:", len(clips))
    seen_paths = set()
    duplicates_to_delete = []
    
    for c in clips:
        props = c.GetClipProperty()
        p = props.get("File Path", "") if props else ""
        norm_p = os.path.normpath(p).lower() if p else c.GetName()
        if norm_p in seen_paths:
            duplicates_to_delete.append(c)
        else:
            seen_paths.add(norm_p)
            
    print(f"Unique clips: {len(seen_paths)}, Duplicates to remove: {len(duplicates_to_delete)}")
    if duplicates_to_delete:
        print("Testing deleting 1 duplicate clip:", duplicates_to_delete[0].GetName())
        del_res = mp.DeleteClips([duplicates_to_delete[0]])
        print("DeleteClips result:", del_res)
        print("New clip count in folder:", len(vfolder.GetClipList()))
