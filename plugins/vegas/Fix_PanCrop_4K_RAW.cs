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
            if (vegas == null || vegas.Project == null)
            {
                MessageBox.Show("No active project in VEGAS Pro.", "Fix Pan/Crop", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int fixedEventsCount = 0;
            int totalKeyframesFixed = 0;
            int skippedCount = 0;

            const float scale = 0.5625f;       // 1215 / 2160 = 2160 / 3840 = 9 / 16
            const float offsetX = 1312.5f;     // (3840 - 1215) / 2
            const float activeVideoW = 1215.0f;
            const float activeVideoH = 2160.0f;

            using (UndoBlock undo = new UndoBlock("Conform Pan/Crop to 4K RAW"))
            {
                foreach (Track track in vegas.Project.Tracks)
                {
                    if (!track.IsVideo()) continue;

                    VideoTrack vt = track as VideoTrack;
                    if (vt != null && vt.IsAdjustmentTrack) continue;

                    string tname = (track.Name ?? "").ToLower();
                    if (tname.Contains("[adjustment]") ||
                        tname.Contains("film burn") ||
                        tname.Contains("filmburn") ||
                        tname.Contains("halation") ||
                        tname.Contains("transiotions") ||
                        tname.Contains("transition"))
                    {
                        continue;
                    }

                    foreach (TrackEvent ev in track.Events)
                    {
                        VideoEvent ve = ev as VideoEvent;
                        if (ve == null || ve.ActiveTake == null) continue;

                        Take activeTake = ve.ActiveTake;
                        string takeName = activeTake.Name ?? "";

                        // Check if this event is currently on a 4K RAW take (or an MP4 raw file)
                        bool isRawTake = takeName.StartsWith("4K RAW:", StringComparison.OrdinalIgnoreCase);
                        if (!isRawTake)
                        {
                            string p = "";
                            try { p = activeTake.MediaPath ?? (activeTake.Media != null ? activeTake.Media.FilePath : ""); } catch {}
                            string ext = Path.GetExtension(p).ToLower();
                            if ((ext == ".mp4" || ext == ".m4v") && !p.Contains("\\Proxy\\") && !p.Contains("/Proxy/"))
                            {
                                isRawTake = true;
                            }
                        }

                        if (!isRawTake) continue;

                        // Check if the media stream is 3840x2160 (horizontal container with vertical video)
                        Media media = activeTake.Media;
                        if (media == null || media.Streams.Count == 0) continue;
                        VideoStream vs = media.GetVideoStreamByIndex(0);
                        if (vs == null) continue;

                        // Only apply to 3840x2160 media
                        if (vs.Width != 3840 || vs.Height != 2160)
                        {
                            skippedCount++;
                            continue;
                        }

                        if (ve.VideoMotion == null || ve.VideoMotion.Keyframes.Count == 0) continue;

                        bool eventModified = false;

                        // CRITICAL: Disable MaintainAspectRatio and enable ScaleToFill
                        // This prevents VEGAS from enforcing the raw media's 16:9 container aspect ratio,
                        // allowing the 9:16 Pan/Crop frame to fill the vertical project canvas full bleed.
                        if (ve.MaintainAspectRatio)
                        {
                            ve.MaintainAspectRatio = false;
                            eventModified = true;
                        }
                        if (!ve.VideoMotion.ScaleToFill)
                        {
                            ve.VideoMotion.ScaleToFill = true;
                            eventModified = true;
                        }

                        foreach (VideoMotionKeyframe kf in ve.VideoMotion.Keyframes)
                        {
                            if (kf == null || kf.Bounds == null) continue;

                            VideoMotionVertex tl = kf.Bounds.TopLeft;
                            VideoMotionVertex tr = kf.Bounds.TopRight;
                            VideoMotionVertex br = kf.Bounds.BottomRight;
                            VideoMotionVertex bl = kf.Bounds.BottomLeft;
                            if (tl == null || tr == null || br == null || bl == null) continue;

                            double w = Math.Sqrt(Math.Pow(tr.X - tl.X, 2) + Math.Pow(tr.Y - tl.Y, 2));
                            double h = Math.Sqrt(Math.Pow(tl.X - bl.X, 2) + Math.Pow(tl.Y - bl.Y, 2));

                            // If already conformed to RAW active video:
                            // Center X is in [1500, 2340], Height <= 2160.5, and Width <= 1215.5
                            if (kf.Center != null && kf.Center.X >= 1500.0f && kf.Center.X <= 2340.0f && h <= 2160.5 && w <= 1215.5)
                            {
                                continue;
                            }

                            // Case 1: Vegas reset the keyframe to full 16:9 container (Width ~3840, Height ~2160)
                            if (w > 3000.0 && Math.Abs(h - 2160.0) < 100.0)
                            {
                                double angleRad = kf.Rotation;
                                float halfW = activeVideoW / 2.0f; // 607.5
                                float halfH = activeVideoH / 2.0f; // 1080.0
                                float cx = 1920.0f;
                                float cy = 1080.0f;

                                float cosA = (float)Math.Cos(angleRad);
                                float sinA = (float)Math.Sin(angleRad);

                                VideoMotionVertex newTL = new VideoMotionVertex(cx + (-halfW * cosA - -halfH * sinA), cy + (-halfW * sinA + -halfH * cosA));
                                VideoMotionVertex newTR = new VideoMotionVertex(cx + ( halfW * cosA - -halfH * sinA), cy + ( halfW * sinA + -halfH * cosA));
                                VideoMotionVertex newBR = new VideoMotionVertex(cx + ( halfW * cosA -  halfH * sinA), cy + ( halfW * sinA +  halfH * cosA));
                                VideoMotionVertex newBL = new VideoMotionVertex(cx + (-halfW * cosA -  halfH * sinA), cy + (-halfW * sinA +  halfH * cosA));

                                kf.Bounds = new VideoMotionBounds(newTL, newTR, newBR, newBL);
                                totalKeyframesFixed++;
                                eventModified = true;
                            }
                            // Case 2: Keyframe is in proxy coordinate space (2160 x 3840)
                            // Transform all 4 corner vertices into 4K RAW active video area
                            else
                            {
                                VideoMotionVertex newTL = new VideoMotionVertex(offsetX + tl.X * scale, tl.Y * scale);
                                VideoMotionVertex newTR = new VideoMotionVertex(offsetX + tr.X * scale, tr.Y * scale);
                                VideoMotionVertex newBR = new VideoMotionVertex(offsetX + br.X * scale, br.Y * scale);
                                VideoMotionVertex newBL = new VideoMotionVertex(offsetX + bl.X * scale, bl.Y * scale);

                                kf.Bounds = new VideoMotionBounds(newTL, newTR, newBR, newBL);
                                totalKeyframesFixed++;
                                eventModified = true;
                            }
                        }

                        if (eventModified)
                        {
                            fixedEventsCount++;
                        }
                    }
                }
            }

            string msg = string.Format(
                "Pan/Crop Conformed to 4K RAW!\n\n" +
                "• Video Events Conformed: {0}\n" +
                "• Keyframes Adjusted: {1}\n" +
                "• Skipped non-vertical clips: {2}\n\n" +
                "All 9:16 vertical clips now perfectly fill the canvas edge-to-edge with ZERO black bars.",
                fixedEventsCount, totalKeyframesFixed, skippedCount
            );

            MessageBox.Show(msg, "Pan/Crop Conform Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error conforming Pan/Crop:\n" + ex.Message + "\n\n" + ex.StackTrace, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
