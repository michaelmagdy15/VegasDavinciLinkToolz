import sys
sys.path.insert(0, '.')
from core.live_bridge import get_resolve_app

r = get_resolve_app()
p = r.GetProjectManager().GetCurrentProject()
tl = p.GetTimelineByIndex(3)

print("Auditing all Fusion comps on Timeline 3:")
black_clips = []
for t in range(1, tl.GetTrackCount('video') + 1):
    items = tl.GetItemListInTrack('video', t) or []
    for it in items:
        comp = it.GetFusionCompByIndex(1)
        if comp:
            tools = comp.GetToolList()
            for k in tools:
                if 'Brightness' in tools[k].Name:
                    bc = tools[k]
                    g0 = bc.Gain[0]
                    # Check if Gain stays 0.0 or is 0 at start
                    # Or check Gain at frame 0, 1, 2
                    try:
                        dur = it.GetDuration()
                        g_mid = bc.Gain[int(dur/2)]
                        if g0 == 0.0 and g_mid == 0.0:
                            black_clips.append((t, it.GetName(), it.GetStart(), "Completely Black (Gain=0 all frames)"))
                        elif g0 == 0.0:
                            black_clips.append((t, it.GetName(), it.GetStart(), f"Starts Black (Gain[0]=0, Gain[mid]={g_mid})"))
                    except Exception as e:
                        pass

print(f"Clips with black Gain: {len(black_clips)}")
for t, name, st, reason in black_clips:
    print(f"  V{t}: {name} (start {st}) -> {reason}")
