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
                MessageBox.Show("No active project in VEGAS Pro.", "VEGAS Live Link", MessageBoxButtons.OK, MessageBoxIcon.Warning);
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

            // Export Project Markers
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

            // Export Project Regions
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
                        pan = at.PanX;
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

                    // Extract Pan/Crop Zoom & Rotation
                    double rotationAngle = 0.0;
                    double zoomX = 1.0;
                    double zoomY = 1.0;
                    double panX = 0.0;
                    double panY = 0.0;

                    VideoEvent ve = ev as VideoEvent;
                    if (ve != null && ve.VideoMotion != null && ve.VideoMotion.Keyframes.Count > 0)
                    {
                        VideoMotionKeyframe kf = ve.VideoMotion.Keyframes[0];
                        rotationAngle = kf.Rotation;

                        if (kf.Bounds != null && kf.Bounds.TopRight != null && kf.Bounds.TopLeft != null && kf.Bounds.BottomLeft != null)
                        {
                            double bw = Math.Sqrt(Math.Pow(kf.Bounds.TopRight.X - kf.Bounds.TopLeft.X, 2) + Math.Pow(kf.Bounds.TopRight.Y - kf.Bounds.TopLeft.Y, 2));
                            double bh = Math.Sqrt(Math.Pow(kf.Bounds.BottomLeft.X - kf.Bounds.TopLeft.X, 2) + Math.Pow(kf.Bounds.BottomLeft.Y - kf.Bounds.TopLeft.Y, 2));
                            if (bw > 0.001 && vegas.Project.Video.Width > 0)
                            {
                                zoomX = (double)vegas.Project.Video.Width / bw;
                            }
                            if (bh > 0.001 && vegas.Project.Video.Height > 0)
                            {
                                zoomY = (double)vegas.Project.Video.Height / bh;
                            }
                        }

                        if (kf.Center != null)
                        {
                            panX = (double)kf.Center.X - (vegas.Project.Video.Width / 2.0);
                            panY = (double)kf.Center.Y - (vegas.Project.Video.Height / 2.0);
                        }
                    }

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
                    cb.AppendFormat("          \"rotation_angle\": {0:F2},\n", rotationAngle);
                    cb.AppendFormat("          \"zoom_x\": {0:F4},\n", zoomX);
                    cb.AppendFormat("          \"zoom_y\": {0:F4},\n", zoomY);
                    cb.AppendFormat("          \"pan_x\": {0:F2},\n", panX);
                    cb.AppendFormat("          \"pan_y\": {0:F2},\n", panY);
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

            // Write UTF-8 without BOM to prevent Python JSONDecodeError
            File.WriteAllText(jsonPath, sb.ToString(), new UTF8Encoding(false));

            // Execute Python Live Bridge runner
            string runnerPath = Path.Combine(bridgeDir, "run_live_sync.py");
            bool triggered = false;

            if (File.Exists(runnerPath))
            {
                try
                {
                    string pythonExe = "python";
                    string localPy = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"Programs\Python\Python312\python.exe");
                    if (File.Exists(localPy))
                    {
                        pythonExe = localPy;
                    }

                    ProcessStartInfo psi = new ProcessStartInfo
                    {
                        FileName = pythonExe,
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
