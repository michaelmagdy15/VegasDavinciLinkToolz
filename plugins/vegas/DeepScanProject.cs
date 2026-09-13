using System;
using System.IO;
using System.Text;
using System.Globalization;
using System.Collections;
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
                MessageBox.Show("No active project in VEGAS Pro.", "VEGAS Deep Project Scanner", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            string userDir = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            string bridgeDir = Path.Combine(userDir, ".timeline_bridge");
            if (!Directory.Exists(bridgeDir))
            {
                Directory.CreateDirectory(bridgeDir);
            }

            string jsonPath = Path.Combine(bridgeDir, "vegas_deep_scan.json");
            string mdPath = Path.Combine(bridgeDir, "vegas_deep_scan_summary.md");

            Project proj = vegas.Project;
            int totalVideoTracks = 0;
            int totalAudioTracks = 0;
            int totalEvents = 0;
            int totalKeyframes = 0;
            List<string> detectedPlugins = new List<string>();

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("{");
            sb.AppendFormat(CultureInfo.InvariantCulture, "  \"project_file\": \"{0}\",\n", EscapeJson(proj.FilePath ?? "Untitled"));
            sb.AppendFormat(CultureInfo.InvariantCulture, "  \"project_name\": \"{0}\",\n", EscapeJson(Path.GetFileNameWithoutExtension(proj.FilePath ?? "Untitled")));
            sb.AppendFormat(CultureInfo.InvariantCulture, "  \"scan_timestamp\": \"{0}\",\n", DateTime.UtcNow.ToString("o"));

            // Project Video Settings
            sb.AppendLine("  \"video_settings\": {");
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"width\": {0},\n", proj.Video.Width);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"height\": {0},\n", proj.Video.Height);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"frame_rate\": {0:F4},\n", proj.Video.FrameRate);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"pixel_aspect_ratio\": {0:F4},\n", proj.Video.PixelAspectRatio);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"field_order\": \"{0}\",\n", proj.Video.FieldOrder);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"pixel_format\": \"{0}\",\n", proj.Video.PixelFormat);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"hdr_mode\": \"{0}\",\n", proj.Video.HDRMode);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"motion_blur_type\": \"{0}\"\n", proj.Video.MotionBlurType);
            sb.AppendLine("  },");

            // Project Audio Settings
            sb.AppendLine("  \"audio_settings\": {");
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"sample_rate\": {0},\n", proj.Audio.SampleRate);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"bit_depth\": {0},\n", proj.Audio.BitDepth);
            sb.AppendFormat(CultureInfo.InvariantCulture, "    \"master_bus_mode\": \"{0}\"\n", proj.Audio.MasterBusMode);
            sb.AppendLine("  },");

            // Master Output Video Effects (VideoBus)
            sb.AppendLine("  \"project_video_effects\": [");
            List<string> projVidFxJson = new List<string>();
            if (proj.VideoBus != null && proj.VideoBus.Effects != null)
            {
                foreach (Effect fx in proj.VideoBus.Effects)
                {
                    projVidFxJson.Add(SerializeEffect(fx, detectedPlugins, ref totalKeyframes, "    "));
                }
            }
            sb.AppendLine(string.Join(",\n", projVidFxJson.ToArray()));
            sb.AppendLine("  ],");

            // Master Output Audio Effects (MasterBus)
            sb.AppendLine("  \"project_audio_effects\": [");
            List<string> projAudFxJson = new List<string>();
            if (proj.MasterBus != null && proj.MasterBus.Effects != null)
            {
                foreach (Effect fx in proj.MasterBus.Effects)
                {
                    projAudFxJson.Add(SerializeEffect(fx, detectedPlugins, ref totalKeyframes, "    "));
                }
            }
            sb.AppendLine(string.Join(",\n", projAudFxJson.ToArray()));
            sb.AppendLine("  ],");

            // Markers & Regions
            sb.AppendLine("  \"markers\": [");
            List<string> markerList = new List<string>();
            foreach (Marker m in proj.Markers)
            {
                markerList.Add(string.Format(CultureInfo.InvariantCulture, "    {{\"label\": \"{0}\", \"position_ms\": {1:F2}}}", EscapeJson(m.Label ?? ""), m.Position.ToMilliseconds()));
            }
            sb.AppendLine(string.Join(",\n", markerList.ToArray()));
            sb.AppendLine("  ],");

            sb.AppendLine("  \"regions\": [");
            List<string> regionList = new List<string>();
            foreach (Region r in proj.Regions)
            {
                regionList.Add(string.Format(CultureInfo.InvariantCulture, "    {{\"label\": \"{0}\", \"position_ms\": {1:F2}, \"length_ms\": {2:F2}}}", EscapeJson(r.Label ?? ""), r.Position.ToMilliseconds(), r.Length.ToMilliseconds()));
            }
            sb.AppendLine(string.Join(",\n", regionList.ToArray()));
            sb.AppendLine("  ],");

            // Tracks
            sb.AppendLine("  \"tracks\": [");
            List<string> trackJsonList = new List<string>();

            foreach (Track track in proj.Tracks)
            {
                bool isVideo = track.IsVideo();
                bool isAudio = track.IsAudio();
                if (isVideo) totalVideoTracks++;
                if (isAudio) totalAudioTracks++;

                StringBuilder tb = new StringBuilder();
                tb.AppendLine("    {");
                tb.AppendFormat(CultureInfo.InvariantCulture, "      \"index\": {0},\n", track.Index);
                tb.AppendFormat(CultureInfo.InvariantCulture, "      \"name\": \"{0}\",\n", EscapeJson(track.Name ?? (isVideo ? "Video Track" : "Audio Track")));
                tb.AppendFormat(CultureInfo.InvariantCulture, "      \"is_video\": {0},\n", isVideo ? "true" : "false");
                tb.AppendFormat(CultureInfo.InvariantCulture, "      \"is_audio\": {0},\n", isAudio ? "true" : "false");
                tb.AppendFormat(CultureInfo.InvariantCulture, "      \"mute\": {0},\n", track.Mute ? "true" : "false");
                tb.AppendFormat(CultureInfo.InvariantCulture, "      \"solo\": {0},\n", track.Solo ? "true" : "false");

                if (isVideo)
                {
                    VideoTrack vt = track as VideoTrack;
                    tb.AppendFormat(CultureInfo.InvariantCulture, "      \"composite_mode\": \"{0}\",\n", vt != null ? vt.CompositeMode.ToString() : "SourceAlpha");
                    tb.AppendFormat(CultureInfo.InvariantCulture, "      \"composite_level\": {0:F4},\n", vt != null ? vt.CompositeLevel : 1.0f);
                    tb.AppendFormat(CultureInfo.InvariantCulture, "      \"is_adjustment_track\": {0},\n", (vt != null && vt.IsAdjustmentTrack) ? "true" : "false");

                    // Track Motion Keyframes
                    tb.AppendLine("      \"track_motion_keyframes\": [");
                    List<string> tmkfList = new List<string>();
                    if (vt != null && vt.TrackMotion != null && vt.TrackMotion.MotionKeyframes != null)
                    {
                        foreach (TrackMotionKeyframe tmkf in vt.TrackMotion.MotionKeyframes)
                        {
                            totalKeyframes++;
                            StringBuilder kb = new StringBuilder();
                            kb.AppendLine("        {");
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"position_ms\": {0:F2},\n", tmkf.Position.ToMilliseconds());
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"pos_x\": {0:F3},\n", tmkf.PositionX);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"pos_y\": {0:F3},\n", tmkf.PositionY);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"pos_z\": {0:F3},\n", tmkf.PositionZ);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"rot_x\": {0:F3},\n", tmkf.RotationX);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"rot_y\": {0:F3},\n", tmkf.RotationY);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"rot_z\": {0:F3},\n", tmkf.RotationZ);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"width\": {0:F2},\n", tmkf.Width);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"height\": {0:F2},\n", tmkf.Height);
                            kb.AppendFormat(CultureInfo.InvariantCulture, "          \"smoothness\": {0:F2}\n", tmkf.Smoothness);
                            kb.Append("        }");
                            tmkfList.Add(kb.ToString());
                        }
                    }
                    tb.AppendLine(string.Join(",\n", tmkfList.ToArray()));
                    tb.AppendLine("      ],");
                }

                if (isAudio)
                {
                    AudioTrack at = track as AudioTrack;
                    tb.AppendFormat(CultureInfo.InvariantCulture, "      \"volume_db\": {0:F2},\n", at != null ? at.Volume : 0f);
                    tb.AppendFormat(CultureInfo.InvariantCulture, "      \"pan\": {0:F2},\n", at != null ? at.PanX : 0f);
                }

                // Track Envelopes
                tb.AppendLine("      \"envelopes\": [");
                List<string> envJsonList = new List<string>();
                try
                {
                    foreach (Envelope env in track.Envelopes)
                    {
                        StringBuilder eb = new StringBuilder();
                        eb.AppendLine("        {");
                        eb.AppendFormat(CultureInfo.InvariantCulture, "          \"type\": \"{0}\",\n", env.Type.ToString());
                        eb.AppendFormat(CultureInfo.InvariantCulture, "          \"name\": \"{0}\",\n", EscapeJson(env.Name ?? ""));
                        eb.AppendLine("          \"points\": [");
                        List<string> ptsList = new List<string>();
                        foreach (EnvelopePoint pt in env.Points)
                        {
                            ptsList.Add(string.Format(CultureInfo.InvariantCulture,
                                "            {{\"position_ms\": {0:F2}, \"value\": {1:F4}, \"curve\": \"{2}\"}}",
                                pt.X.ToMilliseconds(), pt.Y, pt.Curve.ToString()));
                        }
                        eb.AppendLine(string.Join(",\n", ptsList.ToArray()));
                        eb.AppendLine("          ]");
                        eb.Append("        }");
                        envJsonList.Add(eb.ToString());
                    }
                }
                catch {}
                tb.AppendLine(string.Join(",\n", envJsonList.ToArray()));
                tb.AppendLine("      ],");

                // Track Effects
                tb.AppendLine("      \"effects\": [");
                List<string> trackFxJson = new List<string>();
                foreach (Effect fx in track.Effects)
                {
                    trackFxJson.Add(SerializeEffect(fx, detectedPlugins, ref totalKeyframes, "        "));
                }
                tb.AppendLine(string.Join(",\n", trackFxJson.ToArray()));
                tb.AppendLine("      ],");

                // Track Events / Clips
                tb.AppendLine("      \"events\": [");
                List<string> eventJsonList = new List<string>();
                foreach (TrackEvent ev in track.Events)
                {
                    totalEvents++;
                    Take take = ev.ActiveTake;
                    string mediaPath = "";
                    string clipName = take != null ? (take.Name ?? "") : "";
                    double inOffsetMs = 0;
                    bool isReversed = (ev.PlaybackRate < 0);

                    if (take != null)
                    {
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

                    double fadeInMs = ev.FadeIn != null ? ev.FadeIn.Length.ToMilliseconds() : 0.0;
                    double fadeOutMs = ev.FadeOut != null ? ev.FadeOut.Length.ToMilliseconds() : 0.0;
                    string fadeInCurve = ev.FadeIn != null ? ev.FadeIn.Curve.ToString() : "None";
                    string fadeOutCurve = ev.FadeOut != null ? ev.FadeOut.Curve.ToString() : "None";
                    float fadeGain = ev.FadeIn != null ? ev.FadeIn.Gain : 1.0f;
                    double playbackRate = Math.Abs(ev.PlaybackRate);
                    if (playbackRate <= 0.001) playbackRate = 1.0;

                    StringBuilder evb = new StringBuilder();
                    evb.AppendLine("        {");
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"name\": \"{0}\",\n", EscapeJson(clipName));
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"media_path\": \"{0}\",\n", EscapeJson(mediaPath));
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"timeline_start_ms\": {0:F2},\n", ev.Start.ToMilliseconds());
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"timeline_length_ms\": {0:F2},\n", ev.Length.ToMilliseconds());
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"source_in_ms\": {0:F2},\n", inOffsetMs);
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"playback_rate\": {0:F4},\n", playbackRate);
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"is_reversed\": {0},\n", isReversed ? "true" : "false");
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"fade_in_ms\": {0:F2},\n", fadeInMs);
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"fade_out_ms\": {0:F2},\n", fadeOutMs);
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"fade_in_curve\": \"{0}\",\n", EscapeJson(fadeInCurve));
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"fade_out_curve\": \"{0}\",\n", EscapeJson(fadeOutCurve));
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"fade_gain\": {0:F3},\n", fadeGain);
                    evb.AppendFormat(CultureInfo.InvariantCulture, "          \"mute\": {0},\n", ev.Mute ? "true" : "false");

                    // Pan / Crop Video Motion
                    VideoEvent ve = ev as VideoEvent;
                    if (ve != null && ve.VideoMotion != null)
                    {
                        evb.AppendLine("          \"pan_crop_keyframes\": [");
                        List<string> pckfList = new List<string>();
                        foreach (VideoMotionKeyframe pckf in ve.VideoMotion.Keyframes)
                        {
                            totalKeyframes++;
                            StringBuilder pcb = new StringBuilder();
                            pcb.AppendLine("            {");
                            pcb.AppendFormat(CultureInfo.InvariantCulture, "              \"position_ms\": {0:F2},\n", pckf.Position.ToMilliseconds());
                            pcb.AppendFormat(CultureInfo.InvariantCulture, "              \"rotation\": {0:F2},\n", pckf.Rotation);
                            pcb.AppendFormat(CultureInfo.InvariantCulture, "              \"smoothness\": {0:F2},\n", pckf.Smoothness);
                            if (pckf.Center != null)
                            {
                                pcb.AppendFormat(CultureInfo.InvariantCulture, "              \"center_x\": {0:F2},\n", pckf.Center.X);
                                pcb.AppendFormat(CultureInfo.InvariantCulture, "              \"center_y\": {0:F2},\n", pckf.Center.Y);
                            }
                            if (pckf.Bounds != null && pckf.Bounds.TopLeft != null && pckf.Bounds.TopRight != null && pckf.Bounds.BottomLeft != null)
                            {
                                double w = Math.Sqrt(Math.Pow(pckf.Bounds.TopRight.X - pckf.Bounds.TopLeft.X, 2) + Math.Pow(pckf.Bounds.TopRight.Y - pckf.Bounds.TopLeft.Y, 2));
                                double h = Math.Sqrt(Math.Pow(pckf.Bounds.TopLeft.X - pckf.Bounds.BottomLeft.X, 2) + Math.Pow(pckf.Bounds.TopLeft.Y - pckf.Bounds.BottomLeft.Y, 2));
                                pcb.AppendFormat(CultureInfo.InvariantCulture, "              \"bounds_width\": {0:F2},\n", w);
                                pcb.AppendFormat(CultureInfo.InvariantCulture, "              \"bounds_height\": {0:F2}\n", h);
                            }
                            else
                            {
                                pcb.AppendLine("              \"bounds_width\": 0.0,\n              \"bounds_height\": 0.0");
                            }
                            pcb.Append("            }");
                            pckfList.Add(pcb.ToString());
                        }
                        evb.AppendLine(string.Join(",\n", pckfList.ToArray()));
                        evb.AppendLine("          ],");
                    }

                    // Event Effects
                    evb.AppendLine("          \"effects\": [");
                    List<string> eventFxJson = new List<string>();
                    if (ve != null)
                    {
                        foreach (Effect fx in ve.Effects)
                        {
                            eventFxJson.Add(SerializeEffect(fx, detectedPlugins, ref totalKeyframes, "            "));
                        }
                    }
                    evb.AppendLine(string.Join(",\n", eventFxJson.ToArray()));
                    evb.AppendLine("          ]");

                    evb.Append("        }");
                    eventJsonList.Add(evb.ToString());
                }
                tb.AppendLine(string.Join(",\n", eventJsonList.ToArray()));
                tb.AppendLine("      ]");

                tb.Append("    }");
                trackJsonList.Add(tb.ToString());
            }

            sb.AppendLine(string.Join(",\n", trackJsonList.ToArray()));
            sb.AppendLine("  ]");
            sb.AppendLine("}");

            // Write JSON UTF-8 without BOM
            File.WriteAllText(jsonPath, sb.ToString(), new UTF8Encoding(false));

            // Generate Markdown Summary
            StringBuilder mdb = new StringBuilder();
            mdb.AppendLine("# VEGAS Pro Deep Project Audit Report");
            mdb.AppendFormat(CultureInfo.InvariantCulture, "\n- **Project:** {0}\n", proj.FilePath ?? "Untitled");
            mdb.AppendFormat(CultureInfo.InvariantCulture, "- **Resolution:** {0}x{1} @ {2:F3} fps\n", proj.Video.Width, proj.Video.Height, proj.Video.FrameRate);
            mdb.AppendFormat(CultureInfo.InvariantCulture, "- **Pixel Format:** {0} (HDR Mode: {1})\n", proj.Video.PixelFormat, proj.Video.HDRMode);
            mdb.AppendFormat(CultureInfo.InvariantCulture, "- **Total Tracks:** {0} ({1} Video, {2} Audio)\n", proj.Tracks.Count, totalVideoTracks, totalAudioTracks);
            mdb.AppendFormat(CultureInfo.InvariantCulture, "- **Total Events/Clips:** {0}\n", totalEvents);
            mdb.AppendFormat(CultureInfo.InvariantCulture, "- **Total Animated Keyframes:** {0}\n", totalKeyframes);
            mdb.AppendLine("\n## Detected Effects & OpenFX (OFX) Plugins");
            if (detectedPlugins.Count == 0)
            {
                mdb.AppendLine("*None detected.*");
            }
            else
            {
                foreach (string plug in detectedPlugins)
                {
                    mdb.AppendFormat("- **`{0}`**\n", plug);
                }
            }
            mdb.AppendLine("\n## Tracks Breakdown");
            foreach (Track t in proj.Tracks)
            {
                string ttype = t.IsVideo() ? "Video" : "Audio";
                mdb.AppendFormat("- Track #{0} [{1}]: **{2}** ({3} events, {4} effects)\n", t.Index + 1, ttype, t.Name ?? "Untitled", t.Events.Count, t.Effects.Count);
                foreach (Effect ef in t.Effects)
                {
                    string pName = ef.PlugIn != null ? ef.PlugIn.Name : (ef.Description ?? "FX");
                    string pSet = "";
                    try { if (ef.CurrentPreset != null) pSet = ef.CurrentPreset.Name ?? ""; } catch {}
                    mdb.AppendFormat("  - FX: `{0}` (OFX: {1}, Preset: `{2}`)\n", pName, ef.IsOFX, pSet);
                }
            }
            File.WriteAllText(mdPath, mdb.ToString(), new UTF8Encoding(false));

            string detectedListStr = string.Join("\n• ", detectedPlugins.ToArray());
            if (string.IsNullOrEmpty(detectedListStr)) detectedListStr = "(None)";
            else detectedListStr = "• " + detectedListStr;

            string msg = string.Format(
                "VEGAS Pro Deep Project Scan Complete!\n\n" +
                "Project: {0}\n" +
                "Video Tracks: {1}\n" +
                "Audio Tracks: {2}\n" +
                "Total Events: {3}\n" +
                "Animated Keyframes: {4}\n\n" +
                "Detected Plugins / OFX:\n{5}\n\n" +
                "Scan saved to:\n{6}",
                Path.GetFileNameWithoutExtension(proj.FilePath ?? "Untitled"),
                totalVideoTracks,
                totalAudioTracks,
                totalEvents,
                totalKeyframes,
                detectedListStr,
                jsonPath
            );

            MessageBox.Show(msg, "VEGAS Deep Project Scanner", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Deep Scan Error: {0}\n\nStack:\n{1}", ex.Message, ex.StackTrace),
                "Deep Scan Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private string SerializeEffect(Effect fx, List<string> detectedPlugins, ref int totalKeyframes, string indent)
    {
        string pName = fx.PlugIn != null ? fx.PlugIn.Name : (fx.Description ?? "Unknown");
        string uniqueId = fx.PlugIn != null ? fx.PlugIn.UniqueID : "";
        string classId = fx.PlugIn != null ? fx.PlugIn.ClassID.ToString() : "";
        bool isOfx = fx.IsOFX;
        string presetName = "";
        try
        {
            if (fx.CurrentPreset != null)
            {
                presetName = fx.CurrentPreset.Name ?? "";
            }
        }
        catch {}
        if (!detectedPlugins.Contains(pName))
        {
            detectedPlugins.Add(pName);
        }

        StringBuilder sb = new StringBuilder();
        sb.AppendLine(indent + "{");
        sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"name\": \"{1}\",\n", indent, EscapeJson(pName));
        sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"unique_id\": \"{1}\",\n", indent, EscapeJson(uniqueId));
        sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"class_id\": \"{1}\",\n", indent, EscapeJson(classId));
        sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"is_ofx\": {1},\n", indent, isOfx ? "true" : "false");
        sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"bypass\": {1},\n", indent, fx.Bypass ? "true" : "false");
        sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"preset\": \"{1}\",\n", indent, EscapeJson(presetName));

        if (isOfx && fx.OFXEffect != null)
        {
            OFXEffect ofx = fx.OFXEffect;
            sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"ofx_label\": \"{1}\",\n", indent, EscapeJson(ofx.Label ?? ""));
            sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"ofx_plugin_path\": \"{1}\",\n", indent, EscapeJson(ofx.PlugInPath ?? ""));
            sb.AppendFormat(CultureInfo.InvariantCulture, "{0}  \"ofx_version\": \"{1}\",\n", indent, ofx.Version != null ? ofx.Version.ToString() : "");
            sb.AppendLine(indent + "  \"parameters\": [");

            List<string> paramJsonList = new List<string>();
            try
            {
                foreach (OFXParameter param in ofx.Parameters)
                {
                    string pType = param.ParameterType.ToString();
                    StringBuilder pb = new StringBuilder();
                    pb.AppendLine(indent + "    {");
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"name\": \"{1}\",\n", indent, EscapeJson(param.Name ?? ""));
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"label\": \"{1}\",\n", indent, EscapeJson(param.Label ?? ""));
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"type\": \"{1}\",\n", indent, pType);
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"enabled\": {1},\n", indent, param.Enabled ? "true" : "false");
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"is_animated\": {1},\n", indent, param.IsAnimated ? "true" : "false");

                    string valStr = "\"\"";
                    string minStr = "null";
                    string maxStr = "null";
                    string defStr = "null";
                    List<string> kfJsonList = new List<string>();

                    // Extract typed values and keyframes
                    if (param is OFXDoubleParameter)
                    {
                        OFXDoubleParameter dp = (OFXDoubleParameter)param;
                        valStr = dp.Value.ToString("F6", CultureInfo.InvariantCulture);
                        minStr = dp.Min.ToString("F6", CultureInfo.InvariantCulture);
                        maxStr = dp.Max.ToString("F6", CultureInfo.InvariantCulture);
                        defStr = dp.Default.ToString("F6", CultureInfo.InvariantCulture);

                        if (dp.Keyframes != null && dp.Keyframes.Count > 0)
                        {
                            foreach (OFXDoubleKeyframe kf in dp.Keyframes)
                            {
                                totalKeyframes++;
                                kfJsonList.Add(string.Format(CultureInfo.InvariantCulture,
                                    "{0}        {{\"position_ms\": {1:F2}, \"value\": {2:F6}, \"interpolation\": \"{3}\"}}",
                                    indent, kf.Time.ToMilliseconds(), kf.Value, kf.Interpolation.ToString()));
                            }
                        }
                    }
                    else if (param is OFXBooleanParameter)
                    {
                        OFXBooleanParameter bp = (OFXBooleanParameter)param;
                        valStr = bp.Value ? "true" : "false";
                        defStr = bp.Default ? "true" : "false";
                    }
                    else if (param is OFXChoiceParameter)
                    {
                        OFXChoiceParameter cp = (OFXChoiceParameter)param;
                        valStr = string.Format("\"{0}\"", EscapeJson(cp.Value != null ? cp.Value.Name : ""));
                        defStr = string.Format("\"{0}\"", EscapeJson(cp.Default != null ? cp.Default.Name : ""));
                    }
                    else if (param is OFXRGBParameter)
                    {
                        OFXRGBParameter rp = (OFXRGBParameter)param;
                        valStr = "{\"r\": " + rp.Value.R.ToString("F4", CultureInfo.InvariantCulture) +
                                 ", \"g\": " + rp.Value.G.ToString("F4", CultureInfo.InvariantCulture) +
                                 ", \"b\": " + rp.Value.B.ToString("F4", CultureInfo.InvariantCulture) + "}";
                    }
                    else if (param is OFXRGBAParameter)
                    {
                        OFXRGBAParameter ap = (OFXRGBAParameter)param;
                        valStr = "{\"r\": " + ap.Value.R.ToString("F4", CultureInfo.InvariantCulture) +
                                 ", \"g\": " + ap.Value.G.ToString("F4", CultureInfo.InvariantCulture) +
                                 ", \"b\": " + ap.Value.B.ToString("F4", CultureInfo.InvariantCulture) +
                                 ", \"a\": " + ap.Value.A.ToString("F4", CultureInfo.InvariantCulture) + "}";
                    }
                    else if (param is OFXIntegerParameter)
                    {
                        OFXIntegerParameter ip = (OFXIntegerParameter)param;
                        valStr = ip.Value.ToString();
                        minStr = ip.Min.ToString();
                        maxStr = ip.Max.ToString();
                        defStr = ip.Default.ToString();
                    }
                    else if (param is OFXDouble2DParameter)
                    {
                        OFXDouble2DParameter d2p = (OFXDouble2DParameter)param;
                        valStr = "{\"x\": " + d2p.Value.X.ToString("F6", CultureInfo.InvariantCulture) +
                                 ", \"y\": " + d2p.Value.Y.ToString("F6", CultureInfo.InvariantCulture) + "}";
                    }
                    else if (param is OFXStringParameter)
                    {
                        OFXStringParameter sp = (OFXStringParameter)param;
                        valStr = string.Format("\"{0}\"", EscapeJson(sp.Value ?? ""));
                    }

                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"value\": {1},\n", indent, valStr);
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"min\": {1},\n", indent, minStr);
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"max\": {1},\n", indent, maxStr);
                    pb.AppendFormat(CultureInfo.InvariantCulture, "{0}      \"default\": {1},\n", indent, defStr);
                    pb.AppendLine(indent + "      \"keyframes\": [");
                    pb.AppendLine(string.Join(",\n", kfJsonList.ToArray()));
                    pb.AppendLine(indent + "      ]");
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
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", " ");
    }
}
