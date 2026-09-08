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
                    "VEGAS ↔ Resolve Live Bridge",
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
            sb.AppendLine("  \"tracks\": [");

            List<string> trackJsonList = new List<string>();

            foreach (Track track in vegas.Project.Tracks)
            {
                StringBuilder tb = new StringBuilder();
                tb.AppendLine("    {");
                tb.AppendFormat("      \"name\": \"{0}\",\n", EscapeJson(track.Name ?? ""));
                tb.AppendFormat("      \"index\": {0},\n", track.Index);
                tb.AppendFormat("      \"is_video\": {0},\n", track.IsVideo() ? "true" : "false");
                tb.AppendFormat("      \"is_audio\": {0},\n", track.IsAudio() ? "true" : "false");
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

                    StringBuilder cb = new StringBuilder();
                    cb.AppendLine("        {");
                    cb.AppendFormat("          \"name\": \"{0}\",\n", EscapeJson(clipName));
                    cb.AppendFormat("          \"media_path\": \"{0}\",\n", EscapeJson(mediaPath));
                    cb.AppendFormat("          \"timeline_start_ms\": {0:F2},\n", ev.Start.ToMilliseconds());
                    cb.AppendFormat("          \"timeline_length_ms\": {0:F2},\n", ev.Length.ToMilliseconds());
                    cb.AppendFormat("          \"source_in_ms\": {0:F2}\n", inOffsetMs);
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

            // Execute Python live bridge if available
            string scriptPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "bridge_receiver.py");
            if (!File.Exists(scriptPath))
            {
                scriptPath = Path.Combine(bridgeDir, "import_from_vegas.py");
            }

            bool executed = false;
            if (File.Exists(scriptPath))
            {
                try
                {
                    ProcessStartInfo psi = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = string.Format("\"{0}\" \"{1}\"", scriptPath, jsonPath),
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };
                    Process.Start(psi);
                    executed = true;
                }
                catch {}
            }

            string msg = executed
                ? "Timeline extracted and sent live to DaVinci Resolve!"
                : "Timeline extracted successfully!\nSaved to: " + jsonPath + "\n\nIn DaVinci Resolve, run 'Import from VEGAS' to load it.";

            MessageBox.Show(
                msg,
                "VEGAS ↔ Resolve Live Bridge",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                "Error sending timeline to DaVinci Resolve:\n" + ex.Message,
                "VEGAS ↔ Resolve Live Bridge Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private string EscapeJson(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "\\r");
    }
}
