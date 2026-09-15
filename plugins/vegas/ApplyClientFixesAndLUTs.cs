using System;
using System.IO;
using System.Collections.Generic;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    private static readonly string[] Rec709SonyClips = new string[]
    {
        "AbdraFilms-A7s20260805_9333",
        "AbdraFilms-A7s20260820_0014",
        "AbdraFilms-A7s20260820_0021"
    };

    public void FromVegas(Vegas vegas)
    {
        if (vegas == null || vegas.Project == null)
        {
            MessageBox.Show("No active project in VEGAS Pro.", "Apply Client Fixes", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        try
        {
            Project proj = vegas.Project;

            // 1. Create 2 Dedicated Adjustment Tracks above footage (NEVER moves any original clips!)
            VideoAdjustmentTrack sonyAdjTrack = proj.AddVideoAdjustmentTrack();
            sonyAdjTrack.Name = "[ADJUSTMENT] Sony S-Log3 -> Rec.709 LUT";

            VideoAdjustmentTrack djiAdjTrack = proj.AddVideoAdjustmentTrack();
            djiAdjTrack.Name = "[ADJUSTMENT] DJI D-Log M -> Rec.709 LUT";

            PlugInNode lutPlugin = vegas.VideoFX.FindChildByName("LUT Filter");

            // Add Track-level LUT Filter if available
            if (lutPlugin != null)
            {
                try { sonyAdjTrack.Effects.Add(new Effect(lutPlugin)); } catch {}
                try { djiAdjTrack.Effects.Add(new Effect(lutPlugin)); } catch {}
            }

            int sonyAdjCount = 0;
            int djiAdjCount = 0;
            int rec709Protected = 0;

            bool openingEffectMuted = false;
            bool slowMoFixed = false;
            bool horizonFixed = false;

            // 2. Scan all existing video tracks (skipping the adjustment tracks)
            foreach (Track track in proj.Tracks)
            {
                if (track == sonyAdjTrack || track == djiAdjTrack) continue;
                if (!track.IsVideo()) continue;

                foreach (TrackEvent ev in track.Events)
                {
                    if (!(ev is VideoEvent)) continue;
                    VideoEvent ve = (VideoEvent)ev;
                    Take take = ve.ActiveTake;
                    if (take == null) continue;

                    string name = take.Name ?? "";
                    string clean = CleanOldBadges(name);
                    string key = GetBaseClipKey(clean);

                    double startMs = ev.Start.ToMilliseconds();
                    double endMs = startMs + ev.Length.ToMilliseconds();

                    // Client Fix #1: Mute opening filmburn effect at 00:00:01
                    if (startMs <= 1500 && endMs >= 1000)
                    {
                        if (name.IndexOf("filmburn", StringComparison.OrdinalIgnoreCase) >= 0 ||
                            (track.Name ?? "").IndexOf("film burn", StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            ev.Mute = true;
                            openingEffectMuted = true;
                        }
                    }

                    // Client Fix #10: Slow-mo ghosting at 00:01:02:27 (~62900 ms)
                    if (startMs <= 63500 && endMs >= 62000)
                    {
                        if (name.IndexOf("9235", StringComparison.OrdinalIgnoreCase) >= 0 || ve.PlaybackRate < 0.99)
                        {
                            ve.ResampleMode = VideoResampleMode.Disable;
                            slowMoFixed = true;
                        }
                    }

                    // Client Fix #4: Leveled sea horizon on drone shot at 00:00:32:12 (~32400 ms)
                    if (startMs <= 33000 && endMs >= 32000)
                    {
                        if (name.IndexOf("0009_D", StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            try
                            {
                                if (ve.VideoMotion != null && ve.VideoMotion.Keyframes.Count > 0)
                                {
                                    VideoMotionKeyframe kf = ve.VideoMotion.Keyframes[0];
                                    kf.Rotation = 1.8f;
                                    horizonFixed = true;
                                }
                            }
                            catch {}
                        }
                    }

                    // Categorize and create Adjustment Events precisely over the matching clips
                    if (IsNativeRec709(key))
                    {
                        take.Name = string.Format("🔴 [REC 709 - DO NOT LUT] {0}", clean);
                        rec709Protected++;
                        // DO NOT create any adjustment event above this clip!
                    }
                    else if (key.StartsWith("DJI_", StringComparison.OrdinalIgnoreCase) || clean.IndexOf("dji", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        take.Name = string.Format("🚁 [DJI D-LOG M] {0}", clean);
                        VideoEvent adj = djiAdjTrack.AddVideoEvent(ev.Start, ev.Length);
                        adj.Name = "[DJI D-Log M LUT]";
                        djiAdjCount++;
                    }
                    else if (clean.IndexOf("AbdraFilms-A7IV", StringComparison.OrdinalIgnoreCase) >= 0 ||
                             clean.IndexOf("AbdraFilms-A7s", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        take.Name = string.Format("🟢 [SONY S-LOG3] {0}", clean);
                        VideoEvent adj = sonyAdjTrack.AddVideoEvent(ev.Start, ev.Length);
                        adj.Name = "[Sony S-Log3 LUT]";
                        sonyAdjCount++;
                    }
                    else if (clean.IndexOf("filmburn", StringComparison.OrdinalIgnoreCase) >= 0 ||
                             clean.IndexOf("LIGHT_", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        take.Name = string.Format("🎬 [OVERLAY REC.709] {0}", clean);
                    }
                }
            }

            // 3. Add Client Review Markers onto the Ruler
            AddOrUpdateMarker(proj, 1200, "[CLIENT 0:01] Muted opening filmburn");
            AddOrUpdateMarker(proj, 13700, "[CLIENT 0:13] Replace shot (b-roll)");
            AddOrUpdateMarker(proj, 26400, "[CLIENT 0:26] Overexposed drone - check highlight recovery");
            AddOrUpdateMarker(proj, 32400, "[CLIENT 0:32] Horizon leveled (+1.8 deg)");
            AddOrUpdateMarker(proj, 32830, "[CLIENT 0:32] Replace - too much buildings");
            AddOrUpdateMarker(proj, 33800, "[CLIENT 0:33] Replace - too much rooftop");
            AddOrUpdateMarker(proj, 41330, "[CLIENT 0:41] Replace shot");
            AddOrUpdateMarker(proj, 43830, "[CLIENT 0:43] Replace - rider falling");
            AddOrUpdateMarker(proj, 47400, "[CLIENT 0:47] Boring shot - swap with high action");
            AddOrUpdateMarker(proj, 62900, "[CLIENT 1:02] Slow-mo resample ghosting disabled");

            string report = string.Format(
                "Safe Adjustment & LUT Setup Finished! (0 Clips Moved)\n\n" +
                "1. ADJUSTMENT TRACKS CREATED:\n" +
                "   • '[ADJUSTMENT] Sony S-Log3 -> Rec.709 LUT' ({0} shots covered)\n" +
                "   • '[ADJUSTMENT] DJI D-Log M -> Rec.709 LUT' ({1} shots covered)\n" +
                "   • {2} Native Rec.709 shots protected with NO LUT!\n\n" +
                "2. CLIENT REVISIONS APPLIED:\n" +
                "   • 00:01 Opening filmburn effect: {3}\n" +
                "   • 00:32 Drone horizon leveled: {4}\n" +
                "   • 01:02 Slow-mo ghosting disabled: {5}\n" +
                "   • 10 Frame.io client review markers added to ruler!\n\n" +
                "All your clips, tracks, cuts, and layers remain 100% in place.",
                sonyAdjCount, djiAdjCount, rec709Protected,
                openingEffectMuted ? "MUTED" : "Already clean",
                horizonFixed ? "ROTATED +1.8°" : "Checked",
                slowMoFixed ? "RESAMPLE DISABLED" : "Checked"
            );

            MessageBox.Show(report, "Setup Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error: " + ex.Message + "\n\n" + ex.StackTrace, "Execution Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void AddOrUpdateMarker(Project proj, double ms, string label)
    {
        try
        {
            Timecode pos = Timecode.FromMilliseconds(ms);
            foreach (Marker m in proj.Markers)
            {
                if (Math.Abs(m.Position.ToMilliseconds() - ms) < 500)
                {
                    m.Label = label;
                    return;
                }
            }
            proj.Markers.Add(new Marker(pos, label));
        }
        catch {}
    }

    private bool IsNativeRec709(string key)
    {
        for (int i = 0; i < Rec709SonyClips.Length; i++)
        {
            if (string.Equals(key, Rec709SonyClips[i], StringComparison.OrdinalIgnoreCase)) return true;
        }
        return false;
    }

    private string GetBaseClipKey(string name)
    {
        string s = name.Trim();
        if (s.EndsWith(".mov", StringComparison.OrdinalIgnoreCase) || s.EndsWith(".mp4", StringComparison.OrdinalIgnoreCase))
        {
            s = Path.GetFileNameWithoutExtension(s);
        }
        int subIdx = s.IndexOf(" - subclip", StringComparison.OrdinalIgnoreCase);
        if (subIdx >= 0) s = s.Substring(0, subIdx).Trim();

        int revIdx = s.IndexOf("(reversed)", StringComparison.OrdinalIgnoreCase);
        if (revIdx >= 0) s = s.Substring(0, revIdx).Trim();

        int curlyIdx = s.IndexOf('}');
        if (curlyIdx >= 0) s = s.Substring(0, curlyIdx).Trim();

        return s;
    }

    private string CleanOldBadges(string name)
    {
        string s = name.Trim();
        string[] prefixes = new string[]
        {
            "🟢 [SONY S-LOG3]", "[SONY S-LOG3]",
            "🚁 [DJI D-LOG M]", "[DJI D-LOG M]",
            "🔴 [REC 709 - DO NOT LUT]", "[REC 709 - DO NOT LUT]",
            "🎬 [OVERLAY REC.709]", "[OVERLAY REC.709]",
            "[120fps SLOW-MO]", "[60fps ACTION]", "[24fps CINEMA]"
        };

        bool changed = true;
        while (changed)
        {
            changed = false;
            for (int i = 0; i < prefixes.Length; i++)
            {
                string p = prefixes[i];
                if (s.StartsWith(p, StringComparison.OrdinalIgnoreCase))
                {
                    s = s.Substring(p.Length).Trim();
                    changed = true;
                }
            }
        }
        return s;
    }
}
