using System;
using System.IO;
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
                MessageBox.Show("No active project found in VEGAS Pro.", "Replace Marker 10-11 Cut", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Project proj = vegas.Project;

            // Target cut at 00:00:42;07 (~42.3s - 43.2s) between Marker 10 & 11
            double targetMs = 42600.0;
            string targetHint = "9212";
            string replacementPath = @"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8114.MP4";
            double sourceOffsetMs = 60800.0; // 60.8s: Soaring mid-air apex with ARROW board
            string takeTitle = "Mid-Air Jump Apex - ARROW Board (A7 IV @ 60.8s)";

            if (!File.Exists(replacementPath))
            {
                MessageBox.Show("Replacement footage file not found at:\n" + replacementPath, "File Missing", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            VideoEvent targetEvent = FindTargetEvent(proj, targetMs, targetHint);
            if (targetEvent == null)
            {
                MessageBox.Show("Could not find video clip '9212' near 00:00:42;07 between Markers 10 & 11.", "Clip Not Found", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            using (UndoBlock undo = new UndoBlock("Replace Blurry Cut Between Markers 10 & 11"))
            {
                // Check if already has this take
                Take existingTake = null;
                foreach (Take t in targetEvent.Takes)
                {
                    if (t.Name != null && t.Name.Contains("Mid-Air Jump Apex"))
                    {
                        existingTake = t;
                        break;
                    }
                }

                if (existingTake != null)
                {
                    existingTake.Offset = Timecode.FromMilliseconds(sourceOffsetMs);
                    targetEvent.ActiveTake = existingTake;
                }
                else
                {
                    Media replacementMedia = proj.MediaPool.AddMedia(replacementPath);
                    if (replacementMedia == null || replacementMedia.Streams.Count == 0)
                    {
                        MessageBox.Show("Failed to add media to project pool.", "Media Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    }

                    VideoStream videoStream = replacementMedia.GetVideoStreamByIndex(0);
                    if (videoStream == null)
                    {
                        MessageBox.Show("No video stream found in replacement media.", "Stream Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    }

                    Take newTake = targetEvent.AddTake(videoStream);
                    newTake.Name = string.Format("⭐ [REPLACED] {0}", takeTitle);
                    newTake.Offset = Timecode.FromMilliseconds(sourceOffsetMs);
                    targetEvent.ActiveTake = newTake;
                }

                // Add or update marker on ruler
                Timecode mPos = Timecode.FromMilliseconds(targetMs);
                bool updatedMarker = false;
                foreach (Marker m in proj.Markers)
                {
                    if (Math.Abs(m.Position.ToMilliseconds() - targetMs) < 800)
                    {
                        m.Label = "[REPLACED 10-11] Mid-Air Apex (8114)";
                        updatedMarker = true;
                        break;
                    }
                }
                if (!updatedMarker)
                {
                    try { proj.Markers.Add(new Marker(mPos, "[REPLACED 10-11] Mid-Air Apex (8114)")); } catch {}
                }
            }

            string msg = "✅ Shot Successfully Replaced!\n\n" +
                         "• Location: 00:00:42;07 (Between Markers 10 & 11)\n" +
                         "• Previous: AbdraFilms-A7s...9212 (Blurry distant silhouette)\n" +
                         "• New Master: AbdraFilms-A7IV...8114.MP4 @ 60.8s\n" +
                         "• Shot Type: Mid-Air Jump Apex with ARROW board displayed\n\n" +
                         "✨ Seamless Continuity:\n" +
                         "41.3s: Jump Launch (8114 @ 58.0s)\n" +
                         "42.3s: Mid-Air Apex (8114 @ 60.8s)\n" +
                         "43.2s: Landed Kiteloop (9230 @ 1.5s)\n\n" +
                         "💡 Tip: Press 'T' on this clip anytime in VEGAS Pro to toggle between the original and new take.";

            MessageBox.Show(msg, "Marker 10-11 Replacement Applied", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error: " + ex.Message + "\n\n" + ex.StackTrace, "Script Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private VideoEvent FindTargetEvent(Project proj, double targetMs, string hint)
    {
        VideoEvent fallback = null;
        foreach (Track t in proj.Tracks)
        {
            if (!t.IsVideo()) continue;
            string tname = (t.Name ?? "").ToLower();
            if (tname.Contains("[adjustment]") || tname.Contains("film burn") || tname.Contains("halation") || tname.Contains("lut"))
                continue;

            foreach (TrackEvent ev in t.Events)
            {
                VideoEvent ve = ev as VideoEvent;
                if (ve == null || ve.ActiveTake == null || ve.ActiveTake.Media == null) continue;

                string mPath = "";
                try { mPath = ve.ActiveTake.Media.FilePath ?? ""; } catch {}

                double s = ev.Start.ToMilliseconds();
                double e = s + ev.Length.ToMilliseconds();

                if (s <= (targetMs + 300) && e >= (targetMs - 300))
                {
                    string clipName = ve.ActiveTake.Name ?? "";
                    if (!string.IsNullOrEmpty(hint))
                    {
                        if (clipName.IndexOf(hint, StringComparison.OrdinalIgnoreCase) >= 0 ||
                            mPath.IndexOf(hint, StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            return ve;
                        }
                    }
                    if (fallback == null && !ev.Mute) fallback = ve;
                }
            }
        }
        return fallback;
    }
}
