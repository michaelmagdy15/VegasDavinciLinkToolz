using System;
using ScriptPortal.Vegas;

public class TestMove
{
    public void MoveClip(Track fromTrack, Track toTrack, TrackEvent ev)
    {
        fromTrack.Events.Remove(ev);
        toTrack.Events.Add(ev);
    }
}
