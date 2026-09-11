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

            Dictionary<TrackEventGroup, int> groupMap = new Dictionary<TrackEventGroup, int>();
            int nextGroupId = 1;

            foreach (Track track in vegas.Project.Tracks)
            {
                bool isVideo = track.IsVideo();
                bool isAudio = track.IsAudio();
                bool isAdjustment = false;
                string compositeMode = "SourceAlpha";
                float compositeLevel = 1.0f;

                double trackMotionPosX = 0.0;
                double trackMotionPosY = 0.0;
                double trackMotionScaleX = 1.0;
                double trackMotionScaleY = 1.0;
                double trackMotionRot = 0.0;

                if (isVideo)
                {
                    VideoTrack vt = track as VideoTrack;
                    if (vt != null)
                    {
                        isAdjustment = vt.IsAdjustmentTrack;
                        compositeMode = vt.CompositeMode.ToString();
                        compositeLevel = vt.CompositeLevel;

                        if (vt.TrackMotion != null && vt.TrackMotion.MotionKeyframes != null && vt.TrackMotion.MotionKeyframes.Count > 0)
                        {
                            TrackMotionKeyframe tmkf = vt.TrackMotion.MotionKeyframes[0];
                            trackMotionPosX = tmkf.PositionX;
                            trackMotionPosY = tmkf.PositionY;
                            trackMotionRot = tmkf.RotationZ;

                            if (vegas.Project.Video.Width > 0 && tmkf.Width > 0)
                            {
                                trackMotionScaleX = (double)vegas.Project.Video.Width / tmkf.Width;
                            }
                            if (vegas.Project.Video.Height > 0 && tmkf.Height > 0)
                            {
                                trackMotionScaleY = (double)vegas.Project.Video.Height / tmkf.Height;
                            }
                        }
                    }
                }

                // Collect Track Effects & LUTs
                List<string> trackFxList = new List<string>();
                foreach (Effect fx in track.Effects)
                {
                    string fxName = fx.PlugIn != null ? fx.PlugIn.Name : (fx.Description ?? "Unknown");
                    string fxPreset = "";
                    try
                    {
                        if (fx.CurrentPreset != null)
                        {
                            fxPreset = fx.CurrentPreset.Name ?? "";
                        }
                    }
                    catch {}
                    trackFxList.Add(string.Format("{{\"name\": \"{0}\", \"preset\": \"{1}\"}}", EscapeJson(fxName), EscapeJson(fxPreset)));
                }

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
                tb.AppendFormat("      \"is_adjustment\": {0},\n", isAdjustment ? "true" : "false");
                tb.AppendFormat("      \"composite_mode\": \"{0}\",\n", EscapeJson(compositeMode));
                tb.AppendFormat("      \"composite_level\": {0:F4},\n", compositeLevel);
                tb.AppendFormat("      \"track_motion_x\": {0:F2},\n", trackMotionPosX);
                tb.AppendFormat("      \"track_motion_y\": {0:F2},\n", trackMotionPosY);
                tb.AppendFormat("      \"track_motion_scale_x\": {0:F4},\n", trackMotionScaleX);
                tb.AppendFormat("      \"track_motion_scale_y\": {0:F4},\n", trackMotionScaleY);
                tb.AppendFormat("      \"track_motion_rot\": {0:F2},\n", trackMotionRot);
                tb.AppendFormat("      \"effects\": [{0}],\n", string.Join(", ", trackFxList.ToArray()));
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
                    bool isReversed = (ev.PlaybackRate < 0);

                    if (take != null)
                    {
                        clipName = take.Name ?? "";
                        if (take.Media != null)
                        {
                            mediaPath = take.MediaPath ?? "";
                            if (string.IsNullOrEmpty(mediaPath) || !File.Exists(mediaPath))
                            {
                                if (!string.IsNullOrEmpty(take.Media.FilePath) && File.Exists(take.Media.FilePath))
                                {
                                    mediaPath = take.Media.FilePath;
                                }
                            }
                        }
                        inOffsetMs = take.Offset.ToMilliseconds();
                        if (clipName.IndexOf("Reverse", StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            isReversed = true;
                        }
                    }

                    // Skip generated clips without valid disk media unless it's an adjustment/title
                    if (string.IsNullOrEmpty(mediaPath) || !File.Exists(mediaPath))
                    {
                        continue;
                    }

                    double fadeInMs = ev.FadeIn != null ? ev.FadeIn.Length.ToMilliseconds() : 0.0;
                    double fadeOutMs = ev.FadeOut != null ? ev.FadeOut.Length.ToMilliseconds() : 0.0;
                    string fadeInCurve = ev.FadeIn != null ? ev.FadeIn.Curve.ToString() : "None";
                    string fadeOutCurve = ev.FadeOut != null ? ev.FadeOut.Curve.ToString() : "None";
                    float fadeGain = ev.FadeIn != null ? ev.FadeIn.Gain : 1.0f;
                    double playbackRate = Math.Abs(ev.PlaybackRate);
                    if (playbackRate <= 0.001) playbackRate = 1.0;

                    // Group / Link tracking
                    int groupId = 0;
                    if (ev.Group != null)
                    {
                        if (!groupMap.ContainsKey(ev.Group))
                        {
                            groupMap[ev.Group] = nextGroupId++;
                        }
                        groupId = groupMap[ev.Group];
                    }
                    else if (ev.SyncEvent != null)
                    {
                        long syncKey = Math.Min(ev.EventID, ev.SyncEvent.EventID);
                        groupId = (int)(Math.Abs(syncKey) % 1000000) + 100000;
                    }
                    else if (!string.IsNullOrEmpty(mediaPath))
                    {
                        groupId = Math.Abs((mediaPath + "_" + ev.Start.ToMilliseconds().ToString("F0")).GetHashCode());
                    }

                    // Audio event properties
                    double eventVolume = 0.0;
                    AudioEvent ae = ev as AudioEvent;
                    if (ae != null)
                    {
                        eventVolume = ae.NormalizeGain;
                    }

                    // Extract Pan/Crop Zoom, Pan, Rotation & Keyframes
                    double rotationAngle = 0.0;
                    double zoomX = 1.0;
                    double zoomY = 1.0;
                    double panX = 0.0;
                    double panY = 0.0;
                    double cropLeft = 0.0;
                    double cropRight = 0.0;
                    double cropTop = 0.0;
                    double cropBottom = 0.0;
                    List<string> motionKfList = new List<string>();

                    VideoEvent ve = ev as VideoEvent;
                    if (ve != null && ve.VideoMotion != null && ve.VideoMotion.Keyframes.Count > 0)
                    {
                        VideoMotionKeyframe kf = ve.VideoMotion.Keyframes[0];
                        rotationAngle = kf.Rotation;

                        VideoStream vs = (take != null && take.MediaStream != null) ? take.MediaStream as VideoStream : null;
                        int mediaW = vs != null ? vs.Width : vegas.Project.Video.Width;
                        int mediaH = vs != null ? vs.Height : vegas.Project.Video.Height;
                        if (mediaW <= 0) mediaW = 1920;
                        if (mediaH <= 0) mediaH = 1080;

                        double defCenterX = mediaW / 2.0;
                        double defCenterY = mediaH / 2.0;

                        double projAspect = (double)vegas.Project.Video.Width / (double)vegas.Project.Video.Height;
                        double mediaAspect = (double)mediaW / (double)mediaH;
                        double defCropW = mediaW;
                        double defCropH = mediaH;

                        if (mediaAspect > projAspect)
                        {
                            defCropH = mediaH;
                            defCropW = mediaH * projAspect;
                        }
                        else
                        {
                            defCropW = mediaW;
                            defCropH = mediaW / projAspect;
                        }

                        if (kf.Bounds != null && kf.Bounds.TopRight != null && kf.Bounds.TopLeft != null && kf.Bounds.BottomLeft != null)
                        {
                            double bw = Math.Sqrt(Math.Pow(kf.Bounds.TopRight.X - kf.Bounds.TopLeft.X, 2) + Math.Pow(kf.Bounds.TopRight.Y - kf.Bounds.TopLeft.Y, 2));

                            if (bw > 1.0 && defCropW > 1.0)
                            {
                                double computedZoom = defCropW / bw;
                                if (Math.Abs(computedZoom - 1.0) > 0.02)
                                {
                                    zoomX = computedZoom;
                                    zoomY = computedZoom;
                                }
                            }
                        }

                        if (kf.Center != null)
                        {
                            double shiftX = kf.Center.X - defCenterX;
                            double shiftY = kf.Center.Y - defCenterY;

                            if (Math.Abs(shiftX) > 2.0)
                            {
                                panX = (shiftX / defCropW) * vegas.Project.Video.Width;
                            }
                            if (Math.Abs(shiftY) > 2.0)
                            {
                                panY = -(shiftY / defCropH) * vegas.Project.Video.Height;
                            }
                        }

                        // Collect multi-keyframe animations with full transform details
                        if (ve.VideoMotion.Keyframes.Count > 1)
                        {
                            foreach (VideoMotionKeyframe mkf in ve.VideoMotion.Keyframes)
                            {
                                double kfZoom = 1.0;
                                double kfPanX = 0.0;
                                double kfPanY = 0.0;

                                if (mkf.Bounds != null && mkf.Bounds.TopRight != null && mkf.Bounds.TopLeft != null)
                                {
                                    double kbw = Math.Sqrt(Math.Pow(mkf.Bounds.TopRight.X - mkf.Bounds.TopLeft.X, 2) + Math.Pow(mkf.Bounds.TopRight.Y - mkf.Bounds.TopLeft.Y, 2));
                                    if (kbw > 1.0 && defCropW > 1.0)
                                    {
                                        kfZoom = defCropW / kbw;
                                    }
                                }

                                if (mkf.Center != null)
                                {
                                    double ksx = mkf.Center.X - defCenterX;
                                    double ksy = mkf.Center.Y - defCenterY;
                                    if (Math.Abs(ksx) > 2.0)
                                    {
                                        kfPanX = (ksx / defCropW) * vegas.Project.Video.Width;
                                    }
                                    if (Math.Abs(ksy) > 2.0)
                                    {
                                        kfPanY = -(ksy / defCropH) * vegas.Project.Video.Height;
                                    }
                                }

                                motionKfList.Add(string.Format("{{\"position_ms\": {0:F2}, \"rotation\": {1:F2}, \"zoom\": {2:F4}, \"pan_x\": {3:F2}, \"pan_y\": {4:F2}, \"smoothness\": {5:F2}}}",
                                    mkf.Position.ToMilliseconds(), mkf.Rotation, kfZoom, kfPanX, kfPanY, mkf.Smoothness));
                            }
                        }
                    }

                    // Collect Event FX & LUTs
                    List<string> eventFxList = new List<string>();
                    if (ve != null)
                    {
                        foreach (Effect fx in ve.Effects)
                        {
                            string fxName = fx.PlugIn != null ? fx.PlugIn.Name : (fx.Description ?? "Unknown");
                            string fxPreset = "";
                            try
                            {
                                if (fx.CurrentPreset != null)
                                {
                                    fxPreset = fx.CurrentPreset.Name ?? "";
                                }
                            }
                            catch {}
                            eventFxList.Add(string.Format("{{\"name\": \"{0}\", \"preset\": \"{1}\"}}", EscapeJson(fxName), EscapeJson(fxPreset)));
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
                    cb.AppendFormat("          \"fade_in_curve\": \"{0}\",\n", EscapeJson(fadeInCurve));
                    cb.AppendFormat("          \"fade_out_curve\": \"{0}\",\n", EscapeJson(fadeOutCurve));
                    cb.AppendFormat("          \"fade_gain\": {0:F3},\n", fadeGain);
                    cb.AppendFormat("          \"playback_rate\": {0:F3},\n", playbackRate);
                    cb.AppendFormat("          \"is_reversed\": {0},\n", isReversed ? "true" : "false");
                    cb.AppendFormat("          \"rotation_angle\": {0:F2},\n", rotationAngle);
                    cb.AppendFormat("          \"zoom_x\": {0:F4},\n", zoomX);
                    cb.AppendFormat("          \"zoom_y\": {0:F4},\n", zoomY);
                    cb.AppendFormat("          \"pan_x\": {0:F2},\n", panX);
                    cb.AppendFormat("          \"pan_y\": {0:F2},\n", panY);
                    cb.AppendFormat("          \"crop_left\": {0:F2},\n", cropLeft);
                    cb.AppendFormat("          \"crop_right\": {0:F2},\n", cropRight);
                    cb.AppendFormat("          \"crop_top\": {0:F2},\n", cropTop);
                    cb.AppendFormat("          \"crop_bottom\": {0:F2},\n", cropBottom);
                    cb.AppendFormat("          \"group_id\": {0},\n", groupId);
                    cb.AppendFormat("          \"volume\": {0:F2},\n", eventVolume);
                    cb.AppendFormat("          \"motion_keyframes\": [{0}],\n", string.Join(", ", motionKfList.ToArray()));
                    cb.AppendFormat("          \"effects\": [{0}],\n", string.Join(", ", eventFxList.ToArray()));
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
