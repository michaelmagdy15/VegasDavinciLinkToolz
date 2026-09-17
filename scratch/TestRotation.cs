using System;
using ScriptPortal.Vegas;

public class TestRotation
{
    public void Test(VideoStream stream)
    {
        VideoRotation rot = stream.Rotation;
        stream.Rotation = VideoRotation.Clockwise90;
        stream.Rotation = VideoRotation.Counterclockwise90;
        stream.Rotation = VideoRotation.None;
    }
}
