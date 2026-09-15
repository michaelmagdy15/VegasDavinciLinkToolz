using System;
using System.IO;
using ScriptPortal.Vegas;

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        PlugInNode plug = vegas.VideoFX.FindChildByName("LUT Filter");
        if (plug == null) return;
        Effect fx = new Effect(plug);
        OFXEffect ofx = fx.OFXEffect;
        if (ofx != null)
        {
            using (StreamWriter sw = new StreamWriter(@"C:\Users\Mi5a\VegasDavinciLinkTool\scratch\lut_params.txt"))
            {
                sw.WriteLine("Plugin: " + plug.Name);
                foreach (OFXParameter p in ofx.Parameters)
                {
                    sw.WriteLine("Param: " + p.Name + " (" + p.Label + ") - Type: " + p.ParameterType.ToString());
                }
            }
        }
    }
}
