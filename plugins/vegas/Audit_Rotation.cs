using System;
using System.IO;
using System.Text;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        try
        {
            if (vegas.Project == null) return;

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("=== MEDIA POOL ROTATION AUDIT ===");

            foreach (Media m in vegas.Project.MediaPool)
            {
                string fp = null;
                try { fp = m.FilePath; } catch {}
                if (string.IsNullOrEmpty(fp)) continue;

                if (m.Streams.Count > 0)
                {
                    VideoStream vs = m.GetVideoStreamByIndex(0);
                    if (vs != null)
                    {
                        sb.AppendLine(string.Format("File: {0}", Path.GetFileName(fp)));
                        sb.AppendLine(string.Format("  Dimensions: {0}x{1}", vs.Width, vs.Height));
                        sb.AppendLine(string.Format("  Rotation: {0}", vs.Rotation.ToString()));
                        sb.AppendLine(string.Format("  PAR: {0:F4}", vs.PixelAspectRatio));
                    }
                }
            }

            sb.AppendLine("\n=== TRACK & EVENT AUDIT ===");
            foreach (Track t in vegas.Project.Tracks)
            {
                if (!t.IsVideo()) continue;
                sb.AppendLine(string.Format("Track {0}: '{1}'", t.Index, t.Name));
                foreach (TrackEvent ev in t.Events)
                {
                    VideoEvent ve = ev as VideoEvent;
                    if (ve == null || ve.ActiveTake == null || ve.ActiveTake.Media == null) continue;
                    VideoStream vs = ve.ActiveTake.Media.GetVideoStreamByIndex(0);
                    sb.AppendLine(string.Format("  Event [{0:F2}s - {1:F2}s]: Take='{2}', MediaRot={3}",
                        ev.Start.ToSeconds(), (ev.Start + ev.Length).ToSeconds(),
                        ve.ActiveTake.Name, vs != null ? vs.Rotation.ToString() : "N/A"));
                }
            }

            string outPath = @"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\vegas_rotation_audit.txt";
            File.WriteAllText(outPath, sb.ToString());
            MessageBox.Show("Saved rotation audit to:\n" + outPath, "Rotation Audit Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error: " + ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
