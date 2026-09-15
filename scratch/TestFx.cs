using System;
using ScriptPortal.Vegas;

public class TestFx
{
    public void AddFx(Vegas vegas, VideoEvent ev)
    {
        PlugInNode plugIn = vegas.VideoFX.FindChildByName("LUT Filter");
        if (plugIn != null)
        {
            Effect fx = new Effect(plugIn);
            ev.Effects.Add(fx);
        }
    }
}
