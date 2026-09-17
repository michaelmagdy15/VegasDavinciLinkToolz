using System;
using System.IO;
using System.Collections.Generic;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    private class ShotReplacement
    {
        public double TargetMs;
        public string TargetClipHint;
        public string ReplacementPath;
        public double SourceOffsetMs;
        public string Title;
        public string Reason;

        public ShotReplacement(double targetMs, string targetClipHint, string replacementPath, double sourceOffsetMs, string title, string reason)
        {
            TargetMs = targetMs;
            TargetClipHint = targetClipHint;
            ReplacementPath = replacementPath;
            SourceOffsetMs = sourceOffsetMs;
            Title = title;
            Reason = reason;
        }
    }

    public void FromVegas(Vegas vegas)
    {
        try
        {
            if (vegas == null || vegas.Project == null)
            {
                MessageBox.Show("No active project in VEGAS Pro.", "Auto-Replace Client Shots", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Project proj = vegas.Project;

            // Define the 7 client replacements mapped to exact raw 4K footage on F:\Arrow
            // All offsets are tuned to peak-action frames scouted directly from raw camera files
            List<ShotReplacement> replacements = new List<ShotReplacement>();

            // 1. 00:00:13:21 — Replace beach preparation b-roll
            // Offset 18.0s: Rider close-up on sand in harness, actively pumping & pulling kite
            replacements.Add(new ShotReplacement(
                13700,
                "9209",
                @"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna brolls\AbdraFilms-A7s20260804_9198.MP4",
                18000,
                "Dynamic Kite Pumping (A7S @ 18.0s)",
                "Replaces slow preparation b-roll with high-energy kite pump action"
            ));

            // 2. 00:00:26:12 — Overexposed drone shot
            // Offset 125.0s: Chasing ARROW kite over crystal turquoise Dahab water, 0% sun blowout
            replacements.Add(new ShotReplacement(
                26400,
                "0013_D",
                @"F:\Arrow\arrow kite surf 2\sorted 2\drone\dahab blue lagoon\DJI_20260820170404_0014_D.MP4",
                125000,
                "Balanced Turquoise Drone (DJI @ 125.0s)",
                "Replaces overexposed water glare with balanced sun exposure and deep turquoise water"
            ));

            // 3. 00:00:32:25 — Drone showing Sokhna shoreline buildings
            // Offset 30.0s: Pure open turquoise lagoon, mountain backdrop, 0 resort buildings
            replacements.Add(new ShotReplacement(
                32830,
                "0068_D",
                @"F:\Arrow\arrow kite surf 2\sorted 2\drone\dahab blue lagoon\DJI_20260820142651_0001_D.MP4",
                30000,
                "Dahab Open Turquoise Lagoon (DJI @ 30.0s)",
                "Replaces shoreline resort buildings with pure turquoise open water and mountains"
            ));

            // 4. 00:00:33:24 — Drone showing resort bungalows / rooftops
            // Offset 1.5s: Low-altitude water chase right behind rider skimming across lagoon
            replacements.Add(new ShotReplacement(
                33800,
                "0004_D",
                @"F:\Arrow\arrow kite surf 2\sorted 2\drone\dahab blue lagoon\DJI_20260820171112_0017_D.MP4",
                1500,
                "Low-Water Twin-Tip Chase (DJI @ 1.5s)",
                "Replaces resort rooftops with low-altitude water chase tracking rider"
            ));

            // 5. 00:00:41:10 — Pacing transition
            // Offset 58.0s: High-flying athletic aerial trick in mid-air (A7 IV 4K)
            replacements.Add(new ShotReplacement(
                41330,
                "9212",
                @"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8114.MP4",
                58000,
                "High-Flying Mid-Air Jump (A7 IV @ 58.0s)",
                "Replaces pacing transition with high-energy aerial trick with board extended"
            ));

            // 5b. 00:00:42:07 — Blurry Silhouette Cut (Between Markers 10 & 11)
            // Offset 60.8s: Mid-Air Apex Soar (A7 IV 4K) — Rider soaring at peak jump height with ARROW board displayed
            replacements.Add(new ShotReplacement(
                42275,
                "9212",
                @"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8114.MP4",
                60800,
                "Mid-Air Jump Apex - ARROW Board (A7 IV @ 60.8s)",
                "Replaces blurry distant silhouette with crystal-clear 4K mid-air jump apex"
            ));

            // 6. 00:00:43:25 — Rider stumbling / falling on landing
            // Offset 1.5s: Clean kiteloop landing with carve spray
            replacements.Add(new ShotReplacement(
                43830,
                "9231",
                @"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7s20260804_9230.MP4",
                1500,
                "Clean Landed Kiteloop (A7S @ 1.5s)",
                "Replaces rider stumble with clean landing and spray carve"
            ));

            // 7. 00:00:47:12 — Brand Hero Climax for ARROW Promo (Option A Selected)
            // Offset 26.0s: Aggressive power carve with bold ARROW board logo & explosive rooster-tail spray
            replacements.Add(new ShotReplacement(
                47400,
                "9382",
                @"F:\Arrow\arrow kitesurf\sorted\5 the all open the chest and start kiting\sokhna kiting\AbdraFilms-A7IV20260804_8121.MP4",
                26000,
                "Hero Power Carve - ARROW Board (A7 IV @ 26.0s)",
                "Replaces distant cruising with close-up aggressive carve showcasing the ARROW board"
            ));

            int replacedCount = 0;
            List<string> logEntries = new List<string>();

            using (UndoBlock undo = new UndoBlock("Auto-Replace Client Shots"))
            {
                // Process each replacement
                foreach (ShotReplacement rep in replacements)
                {
                    if (!File.Exists(rep.ReplacementPath))
                    {
                        logEntries.Add(string.Format("❌ File not found: {0}", Path.GetFileName(rep.ReplacementPath)));
                        continue;
                    }

                    VideoEvent targetEvent = FindTargetVideoEvent(proj, rep.TargetMs, rep.TargetClipHint);
                    if (targetEvent == null)
                    {
                        logEntries.Add(string.Format("⚠️ No matching video event found near {0:F1}s", rep.TargetMs / 1000.0));
                        continue;
                    }

                    try
                    {
                        // Check if take already exists on this event
                        Take existingTake = null;
                        foreach (Take tk in targetEvent.Takes)
                        {
                            if (tk.Name != null && (tk.Name.Contains(rep.Title) || tk.Name.Contains("[REPLACED]")))
                            {
                                existingTake = tk;
                                break;
                            }
                            if (tk.MediaPath != null && tk.MediaPath.Equals(rep.ReplacementPath, StringComparison.OrdinalIgnoreCase))
                            {
                                existingTake = tk;
                                break;
                            }
                        }

                        if (existingTake != null)
                        {
                            // Update offset to dialed frame and set active
                            existingTake.Offset = Timecode.FromMilliseconds(rep.SourceOffsetMs);
                            existingTake.Name = string.Format("⭐ [REPLACED] {0}", rep.Title);
                            targetEvent.ActiveTake = existingTake;
                            replacedCount++;
                            AddOrUpdateMarker(proj, rep.TargetMs, string.Format("[REPLACED] {0}", rep.Title));
                            logEntries.Add(string.Format("✅ {0:F1}s: Updated \"{1}\"\n   Reason: {2}",
                                rep.TargetMs / 1000.0, rep.Title, rep.Reason));
                            continue;
                        }

                        // Reuse media from pool if already loaded, or add it
                        Media replacementMedia = null;
                        foreach (Media m in proj.MediaPool)
                        {
                            try
                            {
                                if (m != null && string.Equals(m.FilePath, rep.ReplacementPath, StringComparison.OrdinalIgnoreCase))
                                {
                                    replacementMedia = m;
                                    break;
                                }
                            }
                            catch {}
                        }

                        if (replacementMedia == null)
                        {
                            replacementMedia = proj.MediaPool.AddMedia(rep.ReplacementPath);
                        }

                        if (replacementMedia == null || replacementMedia.Streams.Count == 0)
                        {
                            logEntries.Add(string.Format("❌ Failed to load media stream: {0}", Path.GetFileName(rep.ReplacementPath)));
                            continue;
                        }

                        VideoStream videoStream = replacementMedia.GetVideoStreamByIndex(0);
                        if (videoStream == null)
                        {
                            logEntries.Add(string.Format("❌ No video stream in: {0}", Path.GetFileName(rep.ReplacementPath)));
                            continue;
                        }

                        // Add as a new Take to the event
                        Take newTake = targetEvent.AddTake(videoStream);
                        newTake.Name = string.Format("⭐ [REPLACED] {0}", rep.Title);
                        newTake.Offset = Timecode.FromMilliseconds(rep.SourceOffsetMs);

                        // Set as active take so it immediately plays
                        targetEvent.ActiveTake = newTake;
                        replacedCount++;

                        // Add or update marker on ruler
                        AddOrUpdateMarker(proj, rep.TargetMs, string.Format("[REPLACED] {0}", rep.Title));

                        logEntries.Add(string.Format("✅ {0:F1}s: Swapped with \"{1}\"\n   Reason: {2}",
                            rep.TargetMs / 1000.0, rep.Title, rep.Reason));
                    }
                    catch (Exception ex)
                    {
                        logEntries.Add(string.Format("❌ Error swapping at {0:F1}s: {1}", rep.TargetMs / 1000.0, ex.Message));
                    }
                }
            }

            string report = string.Format(
                "Auto-Replace Client Shots Complete!\n\n" +
                "• Successfully Replaced & Tuned Shots: {0} / {1}\n\n" +
                "Summary:\n{2}\n\n" +
                "💡 Pro-Tip in VEGAS Pro:\n" +
                "Every replaced shot was added as a new Active Take!\n" +
                "You can click on any replaced event and press 'T' to toggle back and forth between the original and new shot.",
                replacedCount, replacements.Count, string.Join("\n\n", logEntries.ToArray())
            );

            MessageBox.Show(report, "Client Revisions Applied", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Execution Error: " + ex.Message + "\n\n" + ex.StackTrace, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private VideoEvent FindTargetVideoEvent(Project proj, double targetMs, string hint)
    {
        VideoEvent fallback = null;

        foreach (Track t in proj.Tracks)
        {
            if (!t.IsVideo()) continue;

            // Skip adjustment tracks, overlay tracks, or grading buses
            string tname = (t.Name ?? "").ToLower();
            if (tname.Contains("[adjustment]") ||
                tname.Contains("film burn") ||
                tname.Contains("filmburn") ||
                tname.Contains("halation") ||
                tname.Contains("lut") ||
                tname.Contains("transiotions") ||
                tname.Contains("transition"))
            {
                continue;
            }

            foreach (TrackEvent ev in t.Events)
            {
                VideoEvent ve = ev as VideoEvent;
                if (ve == null) continue;

                // CRITICAL: Must be a real video clip with media, NOT an empty adjustment or generated media
                if (ve.ActiveTake == null || ve.ActiveTake.Media == null) continue;

                string mediaPath = "";
                try
                {
                    mediaPath = ve.ActiveTake.Media.FilePath ?? "";
                }
                catch {}

                if (string.IsNullOrEmpty(mediaPath)) continue;

                double start = ev.Start.ToMilliseconds();
                double end = start + ev.Length.ToMilliseconds();

                if (start <= (targetMs + 300) && end >= (targetMs - 300))
                {
                    string clipName = ve.ActiveTake.Name ?? "";

                    // If hint provided, check match on clip name and media path
                    if (!string.IsNullOrEmpty(hint))
                    {
                        if (clipName.IndexOf(hint, StringComparison.OrdinalIgnoreCase) >= 0 ||
                            mediaPath.IndexOf(hint, StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            return ve;
                        }
                    }

                    if (fallback == null && !ev.Mute)
                    {
                        fallback = ve;
                    }
                }
            }
        }

        return fallback;
    }

    private void AddOrUpdateMarker(Project proj, double ms, string label)
    {
        try
        {
            Timecode pos = Timecode.FromMilliseconds(ms);
            foreach (Marker m in proj.Markers)
            {
                if (Math.Abs(m.Position.ToMilliseconds() - ms) < 1000)
                {
                    m.Label = label;
                    return;
                }
            }
            proj.Markers.Add(new Marker(pos, label));
        }
        catch {}
    }
}
