/**
 * SendToResolve.cs — VEGAS Pro C# Scripting Extension
 * 
 * Direct one-click Live Link from VEGAS Pro to DaVinci Resolve Studio.
 * Extracts:
 *   - Video & Audio tracks with names, indexes, Mute, Solo
 *   - Audio track Volumes (dB) and Pan
 *   - Every cut with millisecond timeline start, duration, source In-offset
 *   - Playback rate (clip speed / retime)
 *   - Fade-in and Fade-out lengths
 *   - Timeline Markers and Regions (labels, timecodes)
 * 
 * Install location:
 *   %APPDATA%\VEGAS Pro\2026.0\Script Menu\Send to DaVinci Resolve.cs
 * (Also supports VEGAS Pro 22.0, 23.0, etc.)
 */

using System;
using System.IO;
using System.Text;
using System.Diagnostics;
using System.Collections.Generic;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        try
        {
            if (vegas.Project == null)
            {
                MessageBox.Show(
                    "No active project in VEGAS Pro.\nPlease open a project first.",
                    "VEGAS ↔ Resolve Live Link",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
                return;
            }

            string bridgeDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".timeline_bridge");
            if (!Directory.Exists(bridgeDir))
            {
                Directory.CreateDirectory(bridgeDir);
            }

            string jsonPath = Path.Combine(bridgeDir, "vegas_timeline.json");

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("{");
            sb.AppendFormat("  \"project_name\": \"{0}\",\n", EscapeJson(Path.GetFileNameWithoutExtension(vegas.Project.FilePath ?? "Untitled")));
            sb.AppendFormat("  \"frame_rate\": {0:F4},\n", vegas.Project.Video.FrameRate);
            sb.AppendFormat("  \"width\": {0},\n", vegas.Project.Video.Width);
            sb.AppendFormat("  \"height\": {0},\n", vegas.Project.Video.Height);

            // Export Project Markers & Regions
            sb.AppendLine("  \"markers\": [");
            List<string> markerJsonList = new List<string>();
            foreach (Marker m in vegas.Project.Markers)
            {
                StringBuilder mb = new StringBuilder();
                mb.AppendLine("    {");
                mb.AppendFormat("      \"label\": \"{0}\",\n", EscapeJson(m.Label ?? ""));
                mb.AppendFormat("      \"position_ms\": {0:F2}\n", m.Position.ToMilliseconds());
                mb.Append("    }");
                markerJsonList.Add(mb.ToString());
            }
            sb.AppendLine(string.Join(",\n", markerJsonList.ToArray()));
            sb.AppendLine("  ],");

            sb.AppendLine("  \"regions\": [");
            List<string> regionJsonList = new List<string>();
            foreach (Region r in vegas.Project.Regions)
            {
                StringBuilder rb = new StringBuilder();
                rb.AppendLine("    {");
                rb.AppendFormat("      \"label\": \"{0}\",\n", EscapeJson(r.Label ?? ""));
                rb.AppendFormat("      \"position_ms\": {0:F2},\n", r.Position.ToMilliseconds());
                rb.AppendFormat("      \"length_ms\": {0:F2}\n", r.Length.ToMilliseconds());
                rb.Append("    }");
                regionJsonList.Add(rb.ToString());
            }
            sb.AppendLine(string.Join(",\n", regionJsonList.ToArray()));
            sb.AppendLine("  ],");

            // Export Tracks
            sb.AppendLine("  \"tracks\": [");
            List<string> trackJsonList = new List<string>();

            foreach (Track track in vegas.Project.Tracks)
            {
                bool isVideo = track.IsVideo();
                bool isAudio = track.IsAudio();

                float volumeDb = 0f;
                float pan = 0f;

                if (isAudio)
                {
                    AudioTrack at = track as AudioTrack;
                    if (at != null)
                    {
                        volumeDb = at.Volume;
                        pan = at.Pan;
                    }
                }

                StringBuilder tb = new StringBuilder();
                tb.AppendLine("    {");
                tb.AppendFormat("      \"name\": \"{0}\",\n", EscapeJson(track.Name ?? (isVideo ? "Video Track" : "Audio Track")));
                tb.AppendFormat("      \"index\": {0},\n", track.Index);
                tb.AppendFormat("      \"is_video\": {0},\n", isVideo ? "true" : "false");
                tb.AppendFormat("      \"is_audio\": {0},\n", isAudio ? "true" : "false");
                tb.AppendFormat("      \"mute\": {0},\n", track.Mute ? "true" : "false");
                tb.AppendFormat("      \"solo\": {0},\n", track.Solo ? "true" : "false");
                tb.AppendFormat("      \"volume_db\": {0:F2},\n", volumeDb);
                tb.AppendFormat("      \"pan\": {0:F2},\n", pan);
                tb.AppendLine("      \"clips\": [");

                List<string> clipJsonList = new List<string>();

                foreach (TrackEvent ev in track.Events)
                {
                    Take take = ev.ActiveTake;
                    string mediaPath = "";
                    string clipName = "";
                    double inOffsetMs = 0;

                    if (take != null)
                    {
                        clipName = take.Name ?? "";
                        if (take.Media != null)
                        {
                            mediaPath = take.MediaPath ?? "";
                        }
                        inOffsetMs = take.Offset.ToMilliseconds();
                    }

                    double fadeInMs = ev.FadeIn != null ? ev.FadeIn.Length.ToMilliseconds() : 0.0;
                    double fadeOutMs = ev.FadeOut != null ? ev.FadeOut.Length.ToMilliseconds() : 0.0;
                    double playbackRate = ev.PlaybackRate;

                    StringBuilder cb = new StringBuilder();
                    cb.AppendLine("        {");
                    cb.AppendFormat("          \"name\": \"{0}\",\n", EscapeJson(clipName));
                    cb.AppendFormat("          \"media_path\": \"{0}\",\n", EscapeJson(mediaPath));
                    cb.AppendFormat("          \"timeline_start_ms\": {0:F2},\n", ev.Start.ToMilliseconds());
                    cb.AppendFormat("          \"timeline_length_ms\": {0:F2},\n", ev.Length.ToMilliseconds());
                    cb.AppendFormat("          \"source_in_ms\": {0:F2},\n", inOffsetMs);
                    cb.AppendFormat("          \"fade_in_ms\": {0:F2},\n", fadeInMs);
                    cb.AppendFormat("          \"fade_out_ms\": {0:F2},\n", fadeOutMs);
                    cb.AppendFormat("          \"playback_rate\": {0:F3},\n", playbackRate);
                    cb.AppendFormat("          \"mute\": {0}\n", ev.Mute ? "true" : "false");
                    cb.Append("        }");
                    clipJsonList.Add(cb.ToString());
                }

                tb.AppendLine(string.Join(",\n", clipJsonList.ToArray()));
                tb.AppendLine("      ]");
                tb.Append("    }");
                trackJsonList.Add(tb.ToString());
            }

            sb.AppendLine(string.Join(",\n", trackJsonList.ToArray()));
            sb.AppendLine("  ]");
            sb.AppendLine("}");

            File.WriteAllText(jsonPath, sb.ToString(), Encoding.UTF8);

            // Execute Python Live Bridge runner
            string runnerPath = Path.Combine(bridgeDir, "run_live_sync.py");
            bool triggered = false;

            if (File.Exists(runnerPath))
            {
                try
                {
                    ProcessStartInfo psi = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = string.Format("\"{0}\" \"{1}\"", runnerPath, jsonPath),
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };
                    Process.Start(psi);
                    triggered = true;
                }
                catch {}
            }

            string successMsg = triggered
                ? "Timeline sent to DaVinci Resolve!\nDaVinci Resolve is automatically creating and updating your timeline with zero gaps."
                : "Timeline manifest saved!\nPlease run 'ImportFromVegas' in DaVinci Resolve (Workspace > Scripts).";

            MessageBox.Show(successMsg, "VEGAS ↔ Resolve Live Link", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Live Link Error: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Live Link Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private string EscapeJson(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", " ");
    }
}
