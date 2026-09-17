using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Globalization;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        try
        {
            if (vegas == null || vegas.Project == null)
            {
                MessageBox.Show("No active project in VEGAS Pro.");
                return;
            }

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("=== VEGAS VELOCITY & RETIME AUDIT ===");
            sb.AppendLine(string.Format("Project: {0} ({1}x{2} @ {3:F3} fps)",
                vegas.Project.FilePath ?? "Untitled",
                vegas.Project.Video.Width, vegas.Project.Video.Height, vegas.Project.Video.FrameRate));

            int totalClips = 0;
            int velEnvCount = 0;
            int playbackRateCount = 0;
            int fadeCount = 0;

            foreach (Track track in vegas.Project.Tracks)
            {
                if (!track.IsVideo()) continue;
                foreach (TrackEvent ev in track.Events)
                {
                    totalClips++;
                    VideoEvent ve = ev as VideoEvent;
                    bool hasVel = false;
                    List<string> pts = new List<string>();

                    if (ve != null && ve.Envelopes != null && ve.Envelopes.HasEnvelope(EnvelopeType.Velocity))
                    {
                        Envelope vel = ve.Envelopes.FindByType(EnvelopeType.Velocity);
                        if (vel != null && vel.Points.Count > 0)
                        {
                            hasVel = true;
                            velEnvCount++;
                            foreach (EnvelopePoint pt in vel.Points)
                            {
                                pts.Add(string.Format(CultureInfo.InvariantCulture, "[pos={0:F0}ms, val={1:F2}, curve={2}]",
                                    pt.X.ToMilliseconds(), pt.Y, pt.Curve));
                            }
                        }
                    }

                    bool hasRate = Math.Abs(ev.PlaybackRate - 1.0) > 0.01;
                    if (hasRate) playbackRateCount++;

                    double fin = ev.FadeIn != null ? ev.FadeIn.Length.ToMilliseconds() : 0;
                    double fout = ev.FadeOut != null ? ev.FadeOut.Length.ToMilliseconds() : 0;
                    bool hasFade = fin > 10 || fout > 10;
                    if (hasFade) fadeCount++;

                    if (hasVel || hasRate || hasFade)
                    {
                        sb.AppendLine(string.Format("Track {0} ({1}) | Clip '{2}' [{3:F0}ms -> {4:F0}ms]:",
                            track.Index, track.Name, ev.ActiveTake != null ? ev.ActiveTake.Name : "unnamed",
                            ev.Start.ToMilliseconds(), (ev.Start + ev.Length).ToMilliseconds()));
                        if (hasRate) sb.AppendLine(string.Format("   PlaybackRate: {0:F3}x ({1:F0}%)", ev.PlaybackRate, ev.PlaybackRate * 100));
                        if (hasFade) sb.AppendLine(string.Format("   FadeIn: {0:F1}ms, FadeOut: {1:F1}ms", fin, fout));
                        if (hasVel) sb.AppendLine(string.Format("   Velocity Points ({0}): {1}", pts.Count, string.Join(" -> ", pts.ToArray())));
                    }
                }
            }

            sb.AppendLine("\nSummary:");
            sb.AppendLine(string.Format("Total Video Clips: {0}", totalClips));
            sb.AppendLine(string.Format("Clips with Velocity Envelopes: {0}", velEnvCount));
            sb.AppendLine(string.Format("Clips with PlaybackRate != 1.0: {0}", playbackRateCount));
            sb.AppendLine(string.Format("Clips with Fades: {0}", fadeCount));

            string outPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".timeline_bridge", "vegas_velocity_audit.txt");
            File.WriteAllText(outPath, sb.ToString());

            MessageBox.Show(sb.ToString(), "Velocity & Retime Audit", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error: " + ex.Message + "\n" + ex.StackTrace);
        }
    }
}
