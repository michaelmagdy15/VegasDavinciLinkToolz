import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from core.live_bridge import load_manifest_json

data = load_manifest_json(str(Path.home() / '.timeline_bridge' / 'vegas_timeline.json'))
print("Project Name:", data.get("project_name"))
print("Resolution:", data.get("width"), "x", data.get("height"))

sample_clips = []
for t in data.get("tracks", []):
    tname = t.get("name", "")
    for c in (t.get("clips") or []):
        cname = c.get("name", "")
        mpath = c.get("media_path", "")
        zx = c.get("zoom_x")
        px = c.get("pan_x")
        py = c.get("pan_y")
        fxs = [ef.get("name") for ef in c.get("effects", [])]
        if zx != 1.0 or px != 0.0 or py != 0.0 or fxs or "lut" in tname.lower():
            sample_clips.append({
                "track": tname,
                "clip": cname,
                "media": mpath,
                "zoom_x": zx,
                "zoom_y": c.get("zoom_y"),
                "pan_x": px,
                "pan_y": py,
                "effects": fxs,
                "track_fx": [ef.get("name") for ef in t.get("effects", [])]
            })

print(f"Total sampled interesting clips: {len(sample_clips)}")
for sc in sample_clips[:15]:
    print(sc)
