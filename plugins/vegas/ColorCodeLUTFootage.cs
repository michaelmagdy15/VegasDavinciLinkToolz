using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    // The 3 Sony A7S clips confirmed via NonRealTimeMeta XML to be native Rec.709
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
            MessageBox.Show("No active project in VEGAS Pro.", "LUT Assistant", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        try
        {
            // Show interactive choice dialog
            using (Form dialog = new Form())
            {
                dialog.Text = "VEGAS Pro 2026 - Color Code & LUT Assistant";
                dialog.Width = 520;
                dialog.Height = 360;
                dialog.FormBorderStyle = FormBorderStyle.FixedDialog;
                dialog.StartPosition = FormStartPosition.CenterScreen;
                dialog.MaximizeBox = false;
                dialog.MinimizeBox = false;

                Label lblTitle = new Label();
                lblTitle.Text = "Choose how you want to handle your Log & Rec.709 footage:";
                lblTitle.Font = new Font("Segoe UI", 10.5f, FontStyle.Bold);
                lblTitle.SetBounds(20, 15, 460, 30);
                dialog.Controls.Add(lblTitle);

                Label lblDesc = new Label();
                lblDesc.Text = "Detected: Sony A7 IV/S-Log3, Sony A7S III (S-Log3 & 3 Rec.709 shots), DJI D-Log M (Mini 4 Pro), and VFX Overlays.";
                lblDesc.Font = new Font("Segoe UI", 9f, FontStyle.Regular);
                lblDesc.ForeColor = Color.DarkGray;
                lblDesc.SetBounds(20, 48, 460, 35);
                dialog.Controls.Add(lblDesc);

                // Option 1: Tag & Color Code take labels
                Button btnTagOnly = new Button();
                btnTagOnly.Text = "1. Color-Code & Tag Take Labels on Timeline\n(Adds 🟢 S-LOG3, 🚁 DJI D-LOG M, 🔴 REC.709 badges to every clip)";
                btnTagOnly.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);
                btnTagOnly.SetBounds(20, 95, 460, 50);
                btnTagOnly.Click += delegate(object sender, EventArgs e)
                {
                    dialog.DialogResult = DialogResult.Yes;
                    dialog.Close();
                };
                dialog.Controls.Add(btnTagOnly);

                // Option 2: Create Adjustment Events above clips
                Button btnAdjustment = new Button();
                btnAdjustment.Text = "2. Create Adjustment Events with LUT Filter\n(Adds Adjustment Tracks above clips with LUT Filter applied)";
                btnAdjustment.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);
                btnAdjustment.SetBounds(20, 155, 460, 50);
                btnAdjustment.Click += delegate(object sender, EventArgs e)
                {
                    dialog.DialogResult = DialogResult.No;
                    dialog.Close();
                };
                dialog.Controls.Add(btnAdjustment);

                // Option 3: Auto-Move to LUT Tracks
                Button btnMove = new Button();
                btnMove.Text = "3. Auto-Move Clips to Dedicated LUT Tracks\n(Moves S-Log3 -> 'a74 lut', DJI -> 'dji lut', Rec.709 -> 'rec709')";
                btnMove.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);
                btnMove.SetBounds(20, 215, 460, 50);
                btnMove.Click += delegate(object sender, EventArgs e)
                {
                    dialog.DialogResult = DialogResult.Retry;
                    dialog.Close();
                };
                dialog.Controls.Add(btnMove);

                Button btnCancel = new Button();
                btnCancel.Text = "Cancel";
                btnCancel.SetBounds(390, 280, 90, 30);
                btnCancel.Click += delegate(object sender, EventArgs e)
                {
                    dialog.DialogResult = DialogResult.Cancel;
                    dialog.Close();
                };
                dialog.Controls.Add(btnCancel);

                DialogResult dr = dialog.ShowDialog();

                if (dr == DialogResult.Yes)
                {
                    ExecuteColorCoding(vegas, false);
                }
                else if (dr == DialogResult.No)
                {
                    ExecuteAdjustmentEvents(vegas);
                }
                else if (dr == DialogResult.Retry)
                {
                    ExecuteColorCoding(vegas, true);
                }
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error: {0}\n\n{1}", ex.Message, ex.StackTrace),
                "LUT Assistant Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private class EventMovePair
    {
        public Track SourceTrack;
        public Track TargetTrack;
        public TrackEvent Event;
        public EventMovePair(Track src, Track tgt, TrackEvent ev)
        {
            SourceTrack = src;
            TargetTrack = tgt;
            Event = ev;
        }
    }

    private void ExecuteColorCoding(Vegas vegas, bool moveTracks)
    {
        int sonyLogCount = 0;
        int djiCount = 0;
        int rec709Count = 0;
        int overlayCount = 0;

        VideoTrack a74Track = null;
        VideoTrack djiTrack = null;
        VideoTrack rec709Track = null;

        if (moveTracks)
        {
            foreach (Track t in vegas.Project.Tracks)
            {
                if (!t.IsVideo()) continue;
                string lower = (t.Name ?? "").ToLower();
                if (a74Track == null && (lower.Contains("a74 lut") || lower.Contains("a74"))) a74Track = (VideoTrack)t;
                else if (djiTrack == null && (lower.Contains("dji lut") || lower.Contains("dji"))) djiTrack = (VideoTrack)t;
                else if (rec709Track == null && (lower.Contains("rec 709") || lower.Contains("rec709") || lower.Contains("native"))) rec709Track = (VideoTrack)t;
            }

            if (a74Track == null)
            {
                a74Track = vegas.Project.AddVideoTrack();
                a74Track.Name = "a74 lut";
            }
            if (djiTrack == null)
            {
                djiTrack = vegas.Project.AddVideoTrack();
                djiTrack.Name = "dji lut";
            }
            if (rec709Track == null)
            {
                rec709Track = vegas.Project.AddVideoTrack();
                rec709Track.Name = "Sony Rec.709 (No LUT)";
            }
        }

        List<EventMovePair> moveList = new List<EventMovePair>();

        foreach (Track track in vegas.Project.Tracks)
        {
            if (!track.IsVideo()) continue;

            foreach (TrackEvent ev in track.Events)
            {
                if (!(ev is VideoEvent)) continue;
                Take take = ev.ActiveTake;
                if (take == null) continue;

                string rawName = CleanOldBadges(take.Name ?? "");
                string checkKey = GetBaseClipKey(rawName);

                FootageType fType = ClassifyClip(checkKey, rawName);

                if (fType == FootageType.SonySLog3)
                {
                    take.Name = string.Format("🟢 [SONY S-LOG3] {0}", rawName);
                    sonyLogCount++;
                    if (moveTracks && a74Track != null && track != a74Track)
                    {
                        moveList.Add(new EventMovePair(track, a74Track, ev));
                    }
                }
                else if (fType == FootageType.DjiDLogM)
                {
                    take.Name = string.Format("🚁 [DJI D-LOG M] {0}", rawName);
                    djiCount++;
                    if (moveTracks && djiTrack != null && track != djiTrack)
                    {
                        moveList.Add(new EventMovePair(track, djiTrack, ev));
                    }
                }
                else if (fType == FootageType.NativeRec709)
                {
                    take.Name = string.Format("🔴 [REC 709 - DO NOT LUT] {0}", rawName);
                    rec709Count++;
                    if (moveTracks && rec709Track != null && track != rec709Track)
                    {
                        moveList.Add(new EventMovePair(track, rec709Track, ev));
                    }
                }
                else if (fType == FootageType.Overlay)
                {
                    take.Name = string.Format("🎬 [OVERLAY REC.709] {0}", rawName);
                    overlayCount++;
                }
            }
        }

        if (moveTracks && moveList.Count > 0)
        {
            foreach (EventMovePair pair in moveList)
            {
                try
                {
                    pair.SourceTrack.Events.Remove(pair.Event);
                    pair.TargetTrack.Events.Add(pair.Event);
                }
                catch {}
            }
        }

        string summary = string.Format(
            "Color Coding Completed Successfully!\n\n" +
            "• 🟢 Sony S-Log3: {0} clips  --> Apply SLog3 to Rec.709 LUT (Track 'a74 lut')\n" +
            "• 🚁 DJI D-Log M: {1} clips  --> Apply DJI D-Log M to Rec.709 LUT (Track 'dji lut')\n" +
            "• 🔴 Sony Native Rec.709: {2} clips  --> DO NOT APPLY LUT! (9333, 0014, 0021)\n" +
            "• 🎬 VFX Overlays: {3} clips  --> Standard Rec.709\n\n" +
            (moveTracks ? "Clips have been automatically moved to their designated tracks!" : "Take labels on timeline updated with color badges."),
            sonyLogCount, djiCount, rec709Count, overlayCount
        );

        MessageBox.Show(summary, "LUT Footage Classification", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }

    private void ExecuteAdjustmentEvents(Vegas vegas)
    {
        VideoAdjustmentTrack sonyAdjTrack = vegas.Project.AddVideoAdjustmentTrack();
        sonyAdjTrack.Name = "[ADJUSTMENT] Sony S-Log3 -> Rec.709 LUT";

        VideoAdjustmentTrack djiAdjTrack = vegas.Project.AddVideoAdjustmentTrack();
        djiAdjTrack.Name = "[ADJUSTMENT] DJI D-Log M -> Rec.709 LUT";

        PlugInNode lutPlugin = vegas.VideoFX.FindChildByName("LUT Filter");

        int sonyAdjEvents = 0;
        int djiAdjEvents = 0;

        foreach (Track track in vegas.Project.Tracks)
        {
            if (track == sonyAdjTrack || track == djiAdjTrack) continue;
            if (!track.IsVideo()) continue;

            foreach (TrackEvent ev in track.Events)
            {
                if (!(ev is VideoEvent)) continue;
                Take take = ev.ActiveTake;
                if (take == null) continue;

                string rawName = CleanOldBadges(take.Name ?? "");
                string checkKey = GetBaseClipKey(rawName);
                FootageType fType = ClassifyClip(checkKey, rawName);

                if (fType == FootageType.SonySLog3)
                {
                    take.Name = string.Format("🟢 [SONY S-LOG3] {0}", rawName);
                    VideoEvent adjEv = sonyAdjTrack.AddVideoEvent(ev.Start, ev.Length);
                    adjEv.Name = "[LUT] S-Log3 -> Rec.709";
                    if (lutPlugin != null)
                    {
                        try { adjEv.Effects.Add(new Effect(lutPlugin)); } catch {}
                    }
                    sonyAdjEvents++;
                }
                else if (fType == FootageType.DjiDLogM)
                {
                    take.Name = string.Format("🚁 [DJI D-LOG M] {0}", rawName);
                    VideoEvent adjEv = djiAdjTrack.AddVideoEvent(ev.Start, ev.Length);
                    adjEv.Name = "[LUT] DJI D-Log M -> Rec.709";
                    if (lutPlugin != null)
                    {
                        try { adjEv.Effects.Add(new Effect(lutPlugin)); } catch {}
                    }
                    djiAdjEvents++;
                }
                else if (fType == FootageType.NativeRec709)
                {
                    take.Name = string.Format("🔴 [REC 709 - DO NOT LUT] {0}", rawName);
                }
                else if (fType == FootageType.Overlay)
                {
                    take.Name = string.Format("🎬 [OVERLAY REC.709] {0}", rawName);
                }
            }
        }

        string summary = string.Format(
            "Adjustment Tracks & Events Created Successfully!\n\n" +
            "• Created '[ADJUSTMENT] Sony S-Log3 -> Rec.709 LUT' with {0} adjustment events.\n" +
            "• Created '[ADJUSTMENT] DJI D-Log M -> Rec.709 LUT' with {1} adjustment events.\n" +
            "• The 3 native Rec.709 clips (9333, 0014, 0021) were spared from any LUT adjustment!\n\n" +
            "You can now load your .cube LUT files onto the Adjustment Events or Track FX.",
            sonyAdjEvents, djiAdjEvents
        );

        MessageBox.Show(summary, "Adjustment Events Created", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }

    private enum FootageType
    {
        SonySLog3,
        DjiDLogM,
        NativeRec709,
        Overlay,
        Other
    }

    private FootageType ClassifyClip(string key, string fullText)
    {
        for (int i = 0; i < Rec709SonyClips.Length; i++)
        {
            if (string.Equals(key, Rec709SonyClips[i], StringComparison.OrdinalIgnoreCase))
            {
                return FootageType.NativeRec709;
            }
        }

        if (key.StartsWith("DJI_", StringComparison.OrdinalIgnoreCase) || fullText.IndexOf("dji", StringComparison.OrdinalIgnoreCase) >= 0)
        {
            return FootageType.DjiDLogM;
        }

        if (key.IndexOf("AbdraFilms-A7IV", StringComparison.OrdinalIgnoreCase) >= 0 ||
            key.IndexOf("AbdraFilms-A7s", StringComparison.OrdinalIgnoreCase) >= 0)
        {
            return FootageType.SonySLog3;
        }

        if (fullText.IndexOf("filmburn", StringComparison.OrdinalIgnoreCase) >= 0 ||
            fullText.IndexOf("LIGHT_", StringComparison.OrdinalIgnoreCase) >= 0 ||
            fullText.IndexOf("AcidBite", StringComparison.OrdinalIgnoreCase) >= 0 ||
            fullText.IndexOf("logo", StringComparison.OrdinalIgnoreCase) >= 0)
        {
            return FootageType.Overlay;
        }

        return FootageType.Other;
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
