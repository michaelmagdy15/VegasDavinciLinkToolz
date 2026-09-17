using System;
using ScriptPortal.Vegas;

public class TestTakeOffset
{
    public void Test(Take take)
    {
        take.Offset = Timecode.FromMilliseconds(1000.0);
        string name = take.Name;
    }
}
