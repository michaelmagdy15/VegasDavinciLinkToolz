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

                            // Only calculate custom scaling if track motion was actually modified by user
                            bool isDefaultMotion = (Math.Abs(tmkf.PositionX) < 0.001 && Math.Abs(tmkf.PositionY) < 0.001 && Math.Abs(tmkf.RotationZ) < 0.001 && vt.TrackMotion.MotionKeyframes.Count == 1);
                            if (!isDefaultMotion && vegas.Project.Video.Width > 0 && tmkf.Width > 0)
                            {
                                trackMotionScaleX = (double)vegas.Project.Video.Width / tmkf.Width;
                            }
                            else
                            {
                                trackMotionScaleX = 1.0;
                            }

                            if (!isDefaultMotion && vegas.Project.Video.Height > 0 && tmkf.Height > 0)
                            {
                                trackMotionScaleY = (double)vegas.Project.Video.Height / tmkf.Height;
                            }
                            else
                            {
                                trackMotionScaleY = 1.0;
                            }
                        }
                    }
                }

                // Collect Track Effects, OFX & LUTs
                List<string> trackFxList = new List<string>();
                foreach (Effect fx in track.Effects)
                {
                    trackFxList.Add(SerializeEffect(fx, "        "));
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

                        int mediaW = 0;
                        int mediaH = 0;
                        if (take != null && take.Media != null && take.Media.Streams != null)
                        {
                            try
                            {
                                foreach (MediaStream s in take.Media.Streams)
                                {
                                    VideoStream vstr = s as VideoStream;
                                    if (vstr != null && vstr.Width > 0 && vstr.Height > 0)
                                    {
                                        mediaW = vstr.Width;
                                        mediaH = vstr.Height;
                                        break;
                                    }
                                }
                            }
                            catch {}
                        }
                        if (mediaW <= 0) mediaW = vegas.Project.Video.Width;
                        if (mediaH <= 0) mediaH = vegas.Project.Video.Height;
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

                            // If bounds width matches full media or standard project aspect crop, it is default 1.0 fill framing
                            if (Math.Abs(bw - mediaW) < 10.0 || Math.Abs(bw - defCropW) < 10.0 || bw <= 1.0)
                            {
                                zoomX = 1.0;
                                zoomY = 1.0;
                            }
                            else if (defCropW > 1.0)
                            {
                                double computedZoom = defCropW / bw;
                                if (Math.Abs(computedZoom - 1.0) > 0.03)
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

                            // Only assign pan if user explicitly offset center from default
                            if (Math.Abs(shiftX) > 10.0 && defCropW > 1.0)
                            {
                                panX = (shiftX / defCropW) * vegas.Project.Video.Width;
                            }
                            if (Math.Abs(shiftY) > 10.0 && defCropH > 1.0)
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
                                    if (Math.Abs(kbw - mediaW) < 10.0 || Math.Abs(kbw - defCropW) < 10.0 || kbw <= 1.0)
                                    {
                                        kfZoom = 1.0;
                                    }
                                    else if (defCropW > 1.0)
                                    {
                                        kfZoom = defCropW / kbw;
                                    }
                                }

                                if (mkf.Center != null)
                                {
                                    double ksx = mkf.Center.X - defCenterX;
                                    double ksy = mkf.Center.Y - defCenterY;
                                    if (Math.Abs(ksx) > 10.0 && defCropW > 1.0)
                                    {
                                        kfPanX = (ksx / defCropW) * vegas.Project.Video.Width;
                                    }
                                    if (Math.Abs(ksy) > 10.0 && defCropH > 1.0)
                                    {
                                        kfPanY = -(ksy / defCropH) * vegas.Project.Video.Height;
                                    }
                                }

                                motionKfList.Add(string.Format("{{\"position_ms\": {0:F2}, \"rotation\": {1:F2}, \"zoom\": {2:F4}, \"pan_x\": {3:F2}, \"pan_y\": {4:F2}, \"smoothness\": {5:F2}}}",
                                    mkf.Position.ToMilliseconds(), mkf.Rotation, kfZoom, kfPanX, kfPanY, mkf.Smoothness));
                            }
                        }
                    }

                    // Collect Event FX, OFX & LUTs
                    List<string> eventFxList = new List<string>();
                    if (ve != null)
                    {
                        foreach (Effect fx in ve.Effects)
                        {
                            eventFxList.Add(SerializeEffect(fx, "            "));
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
                    string localApp = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                    string[] pyVersions = new string[] { "Python313", "Python312", "Python311", "Python310" };
                    foreach (string ver in pyVersions)
                    {
                        string cand = Path.Combine(localApp, @"Programs\Python\" + ver + @"\python.exe");
                        if (File.Exists(cand))
                        {
                            pythonExe = cand;
                            break;
                        }
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

    private string SerializeEffect(Effect fx, string indent)
    {
        string pName = fx.PlugIn != null ? fx.PlugIn.Name : (fx.Description ?? "Unknown");
        string uniqueId = fx.PlugIn != null ? fx.PlugIn.UniqueID : "";
        string classId = fx.PlugIn != null ? fx.PlugIn.ClassID.ToString() : "";
        bool isOfx = fx.IsOFX;
        string presetName = "";
        try { if (fx.CurrentPreset != null) presetName = fx.CurrentPreset.Name ?? ""; } catch {}

        StringBuilder sb = new StringBuilder();
        sb.AppendLine(indent + "{");
        sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"name\": \"{1}\",\n", indent, EscapeJson(pName));
        sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"unique_id\": \"{1}\",\n", indent, EscapeJson(uniqueId));
        sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"class_id\": \"{1}\",\n", indent, EscapeJson(classId));
        sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"is_ofx\": {1},\n", indent, isOfx ? "true" : "false");
        sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"bypass\": {1},\n", indent, fx.Bypass ? "true" : "false");
        sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"preset\": \"{1}\",\n", indent, EscapeJson(presetName));

        if (isOfx && fx.OFXEffect != null)
        {
            OFXEffect ofx = fx.OFXEffect;
            sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"ofx_label\": \"{1}\",\n", indent, EscapeJson(ofx.Label ?? ""));
            sb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}  \"ofx_plugin_path\": \"{1}\",\n", indent, EscapeJson(ofx.PlugInPath ?? ""));
            sb.AppendLine(indent + "  \"parameters\": [");

            List<string> paramJsonList = new List<string>();
            try
            {
                foreach (OFXParameter param in ofx.Parameters)
                {
                    StringBuilder pb = new StringBuilder();
                    pb.AppendLine(indent + "    {");
                    pb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}      \"name\": \"{1}\",\n", indent, EscapeJson(param.Name ?? ""));
                    pb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}      \"label\": \"{1}\",\n", indent, EscapeJson(param.Label ?? ""));
                    pb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}      \"type\": \"{1}\",\n", indent, param.ParameterType.ToString());
                    pb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}      \"enabled\": {1},\n", indent, param.Enabled ? "true" : "false");

                    string valStr = "\"\"";
                    if (param is OFXDoubleParameter)
                    {
                        valStr = ((OFXDoubleParameter)param).Value.ToString("F6", System.Globalization.CultureInfo.InvariantCulture);
                    }
                    else if (param is OFXBooleanParameter)
                    {
                        valStr = ((OFXBooleanParameter)param).Value ? "true" : "false";
                    }
                    else if (param is OFXChoiceParameter)
                    {
                        OFXChoiceParameter cp = (OFXChoiceParameter)param;
                        valStr = string.Format("\"{0}\"", EscapeJson(cp.Value != null ? cp.Value.Name : ""));
                    }
                    else if (param is OFXRGBParameter)
                    {
                        OFXRGBParameter rp = (OFXRGBParameter)param;
                        valStr = "{\"r\": " + rp.Value.R.ToString("F4", System.Globalization.CultureInfo.InvariantCulture) +
                                 ", \"g\": " + rp.Value.G.ToString("F4", System.Globalization.CultureInfo.InvariantCulture) +
                                 ", \"b\": " + rp.Value.B.ToString("F4", System.Globalization.CultureInfo.InvariantCulture) + "}";
                    }
                    else if (param is OFXRGBAParameter)
                    {
                        OFXRGBAParameter ap = (OFXRGBAParameter)param;
                        valStr = "{\"r\": " + ap.Value.R.ToString("F4", System.Globalization.CultureInfo.InvariantCulture) +
                                 ", \"g\": " + ap.Value.G.ToString("F4", System.Globalization.CultureInfo.InvariantCulture) +
                                 ", \"b\": " + ap.Value.B.ToString("F4", System.Globalization.CultureInfo.InvariantCulture) +
                                 ", \"a\": " + ap.Value.A.ToString("F4", System.Globalization.CultureInfo.InvariantCulture) + "}";
                    }
                    else if (param is OFXIntegerParameter)
                    {
                        valStr = ((OFXIntegerParameter)param).Value.ToString();
                    }
                    else if (param is OFXDouble2DParameter)
                    {
                        OFXDouble2DParameter d2p = (OFXDouble2DParameter)param;
                        valStr = "{\"x\": " + d2p.Value.X.ToString("F6", System.Globalization.CultureInfo.InvariantCulture) +
                                 ", \"y\": " + d2p.Value.Y.ToString("F6", System.Globalization.CultureInfo.InvariantCulture) + "}";
                    }
                    else if (param is OFXStringParameter)
                    {
                        valStr = string.Format("\"{0}\"", EscapeJson(((OFXStringParameter)param).Value ?? ""));
                    }

                    pb.AppendFormat(System.Globalization.CultureInfo.InvariantCulture, "{0}      \"value\": {1}\n", indent, valStr);
                    pb.Append(indent + "    }");
                    paramJsonList.Add(pb.ToString());
                }
            }
            catch {}

            sb.AppendLine(string.Join(",\n", paramJsonList.ToArray()));
            sb.AppendLine(indent + "  ]");
        }
        else
        {
            sb.AppendLine(indent + "  \"parameters\": []");
        }

        sb.Append(indent + "}");
        return sb.ToString();
    }

    private string EscapeJson(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", " ").Replace("\t", " ");
    }
}
