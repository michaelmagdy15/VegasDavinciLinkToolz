using System;
using System.IO;
using System.Collections.Generic;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class TestRemove
{
    public void Test(Vegas vegas)
    {
        List<Track> tracksToRemove = new List<Track>();
        foreach (Track t in vegas.Project.Tracks)
        {
            if (t.IsVideo())
            {
                VideoTrack vt = t as VideoTrack;
                if (vt != null && (vt.IsAdjustmentTrack || (vt.Name != null && vt.Name.Contains("[ADJUSTMENT]"))))
                {
                    tracksToRemove.Add(t);
                }
            }
        }
        foreach (Track t in tracksToRemove)
        {
            vegas.Project.Tracks.Remove(t);
        }

        foreach (Track t in vegas.Project.Tracks)
        {
            for (int i = t.Effects.Count - 1; i >= 0; i--)
            {
                Effect fx = t.Effects[i];
                t.Effects.Remove(fx);
            }

            foreach (TrackEvent ev in t.Events)
            {
                VideoEvent ve = ev as VideoEvent;
                if (ve != null)
                {
                    for (int i = ve.Effects.Count - 1; i >= 0; i--)
                    {
                        ve.Effects.Remove(ve.Effects[i]);
                    }
                }
            }
        }

        foreach (Media m in vegas.Project.MediaPool)
        {
            for (int i = m.Effects.Count - 1; i >= 0; i--)
            {
                m.Effects.Remove(m.Effects[i]);
            }
        }
    }
}
