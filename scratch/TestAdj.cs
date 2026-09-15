using System;
using ScriptPortal.Vegas;

public class TestAdj
{
    public void Test(Vegas vegas)
    {
        VideoAdjustmentTrack adj = vegas.Project.AddVideoAdjustmentTrack();
        adj.Name = "Test Adjustment";
        VideoEvent ev = adj.AddVideoEvent(Timecode.FromMilliseconds(0), Timecode.FromMilliseconds(1000));
        ev.Name = "Test Adj Event";
    }
}
