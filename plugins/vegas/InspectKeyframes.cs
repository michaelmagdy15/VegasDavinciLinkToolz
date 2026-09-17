using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
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
            sb.AppendLine("=== Current Vegas Pan/Crop Inspection ===");
            sb.AppendLine("Time: " + DateTime.Now.ToString("o"));

            foreach (Track track in vegas.Project.Tracks)
            {
                if (!track.IsVideo()) continue;

                foreach (TrackEvent ev in track.Events)
                {
                    VideoEvent ve = ev as VideoEvent;
                    if (ve == null || ve.ActiveTake == null) continue;

                    string takeName = ve.ActiveTake.Name ?? "";
                    if (!takeName.Contains("8227") && !takeName.Contains("0004_D")) continue;

                    sb.AppendLine();
                    sb.AppendLine("Track: " + (track.Name ?? "unnamed"));
                    sb.AppendLine("Event Start: " + ev.Start.ToMilliseconds() + "ms, Take: " + takeName);
                    sb.AppendLine("Takes Count: " + ve.Takes.Count);
                    for (int i = 0; i < ve.Takes.Count; i++)
                    {
                        Take t = ve.Takes[i];
                        string p = "";
                        try { p = t.MediaPath ?? (t.Media != null ? t.Media.FilePath : ""); } catch {}
                        sb.AppendLine(string.Format("  Take [{0}]: {1} | Path: {2}", i, t.Name, p));
                    }

                    if (ve.VideoMotion != null)
                    {
                        sb.AppendLine("VideoMotion.ScaleToFill: " + ve.VideoMotion.ScaleToFill);
                        sb.AppendLine("Keyframes count: " + ve.VideoMotion.Keyframes.Count);
                        for (int k = 0; k < ve.VideoMotion.Keyframes.Count; k++)
                        {
                            VideoMotionKeyframe kf = ve.VideoMotion.Keyframes[k];
                            sb.AppendLine(string.Format("  KF [{0}] Pos={1}ms Rot={2}", k, kf.Position.ToMilliseconds(), kf.Rotation));
                            if (kf.Center != null)
                                sb.AppendLine(string.Format("    Center=({0}, {1})", kf.Center.X, kf.Center.Y));
                            if (kf.Bounds != null)
                            {
                                sb.AppendLine(string.Format("    Bounds TL=({0}, {1}) TR=({2}, {3}) BR=({4}, {5}) BL=({6}, {7})",
                                    kf.Bounds.TopLeft.X, kf.Bounds.TopLeft.Y,
                                    kf.Bounds.TopRight.X, kf.Bounds.TopRight.Y,
                                    kf.Bounds.BottomRight.X, kf.Bounds.BottomRight.Y,
                                    kf.Bounds.BottomLeft.X, kf.Bounds.BottomLeft.Y));
                            }
                        }
                    }
                }
            }

            string outPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".timeline_bridge", "inspect_pancrop.txt");
            File.WriteAllText(outPath, sb.ToString(), new UTF8Encoding(false));
            MessageBox.Show("Inspection saved to:\n" + outPath, "Inspect Keyframes", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error: " + ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
