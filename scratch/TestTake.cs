using System;
using System.IO;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class TestTake
{
    public void Test(Vegas vegas)
    {
        Project proj = vegas.Project;
        if (proj == null) return;
        Media m = proj.MediaPool.AddMedia(@"F:\Arrow\test.mp4");
        VideoStream stream = m.GetVideoStreamByIndex(0);
        foreach (Track t in proj.Tracks)
        {
            foreach (TrackEvent ev in t.Events)
            {
                VideoEvent ve = ev as VideoEvent;
                if (ve != null)
                {
                    Take take = ve.AddTake(stream);
                    ve.ActiveTake = take;
                }
            }
        }
    }
}
