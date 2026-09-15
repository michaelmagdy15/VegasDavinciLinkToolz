using System;
using System.IO;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        if (vegas == null || vegas.Project == null)
        {
            MessageBox.Show("No active project in VEGAS Pro.", "Apply Track LUTs", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        try
        {
            PlugInNode lutPlugin = vegas.VideoFX.FindChildByName("LUT Filter");
            if (lutPlugin == null)
            {
                MessageBox.Show("Could not find 'LUT Filter' plugin in VEGAS Video FX.", "Plugin Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            VideoTrack a74Track = null;
            VideoTrack djiTrack = null;

            foreach (Track t in vegas.Project.Tracks)
            {
                if (!t.IsVideo()) continue;
                string lower = (t.Name ?? "").ToLower();
                if (a74Track == null && (lower.Contains("a74 lut") || lower.Contains("a74"))) a74Track = (VideoTrack)t;
                else if (djiTrack == null && (lower.Contains("dji lut") || lower.Contains("dji"))) djiTrack = (VideoTrack)t;
            }

            if (a74Track == null)
            {
                a74Track = vegas.Project.AddVideoTrack();
                a74Track.Name = "a74 lut";
            }
            if (djiTrack == null)
            {
                djiTrack = vegas.Project.AddVideoTrack();
                djiTrack.Name = "dji lut";
            }

            // Check if LUT Filter already on a74Track
            bool a74HasLut = false;
            foreach (Effect fx in a74Track.Effects)
            {
                if (fx.PlugIn != null && fx.PlugIn.Name.IndexOf("LUT", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    a74HasLut = true;
                    break;
                }
            }
            if (!a74HasLut)
            {
                a74Track.Effects.Add(new Effect(lutPlugin));
            }

            // Check if LUT Filter already on djiTrack
            bool djiHasLut = false;
            foreach (Effect fx in djiTrack.Effects)
            {
                if (fx.PlugIn != null && fx.PlugIn.Name.IndexOf("LUT", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    djiHasLut = true;
                    break;
                }
            }
            if (!djiHasLut)
            {
                djiTrack.Effects.Add(new Effect(lutPlugin));
            }

            string msg = "Track LUT Filters applied successfully!\n\n" +
                         "1. Track 'a74 lut' (Sony S-Log3):\n" +
                         "   -> Added LUT Filter to Track FX.\n" +
                         "   -> In the LUT Filter window, select:\n" +
                         "      C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\LUT\\Sony\\SLog3SGamut3.CineToLC-709TypeA.cube\n\n" +
                         "2. Track 'dji lut' (DJI D-Log M - Drone & Osmo):\n" +
                         "   -> Added LUT Filter to Track FX.\n" +
                         "   -> In the LUT Filter window, select:\n" +
                         "      C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\LUT\\DJI\\DJI Mini 5 Pro D-Log M to Rec.709 LUT.cube\n\n" +
                         "Both tracks now have their native camera conversion LUTs active!";

            MessageBox.Show(msg, "Track LUTs Ready", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error: " + ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
