using System;
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
                MessageBox.Show("No active project in VEGAS Pro.", "Batch Flash Transitions", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Look for Flash transition or Dissolve in VEGAS transitions
            PlugInNode transPlugin = FindPlugin(vegas.Transitions, "Flash");
            if (transPlugin == null) transPlugin = FindPlugin(vegas.Transitions, "Dissolve");
            if (transPlugin == null) transPlugin = FindPlugin(vegas.Transitions, "Crossfade");

            DialogResult prompt = MessageBox.Show(
                "Apply dynamic 6-frame Flash / Fast Transitions across adjacent clips on the selected video track?",
                "Batch Transitions",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );

            if (prompt != DialogResult.Yes) return;

            // 6 frames overlap
            Timecode overlap = Timecode.FromFrames(6);
            int transitionsCreated = 0;

            foreach (Track track in vegas.Project.Tracks)
            {
                if (!track.IsVideo()) continue;
                if (!track.Selected && vegas.Project.Tracks.Count > 1)
                {
                    // If multiple tracks exist and track not selected, skip
                    bool hasSelectedClips = false;
                    foreach (TrackEvent ev in track.Events)
                    {
                        if (ev.Selected) { hasSelectedClips = true; break; }
                    }
                    if (!hasSelectedClips) continue;
                }

                List<TrackEvent> events = new List<TrackEvent>();
                foreach (TrackEvent ev in track.Events) events.Add(ev);
                events.Sort(delegate(TrackEvent a, TrackEvent b) { return a.Start.CompareTo(b.Start); });

                for (int i = 0; i < events.Count - 1; i++)
                {
                    TrackEvent curr = events[i];
                    TrackEvent next = events[i + 1];

                    // Check if touching (gap <= 2 frames)
                    Timecode gap = next.Start - curr.End;
                    if (gap.Nanos <= Timecode.FromFrames(2).Nanos && gap.Nanos >= -Timecode.FromFrames(2).Nanos)
                    {
                        if (next.Length.Nanos > overlap.Nanos * 2 && curr.Length.Nanos > overlap.Nanos * 2)
                        {
                            // Overlap next event back into curr
                            next.Start = curr.End - overlap;
                            next.Length = next.Length + overlap;
                            next.FadeIn.Length = overlap;
                            next.FadeIn.Curve = CurveType.Fast;

                            if (transPlugin != null)
                            {
                                try
                                {
                                    next.FadeIn.Transition = new Effect(transPlugin);
                                }
                                catch {}
                            }

                            transitionsCreated++;
                        }
                    }
                }
            }

            MessageBox.Show(
                string.Format(
                    "Batch Transitions Applied!\n\n" +
                    "- Total Transitions: {0}\n" +
                    "- Duration: 6 frames per cut\n" +
                    "- Transition Effect: {1}",
                    transitionsCreated, (transPlugin != null ? transPlugin.Name : "Fast Action Crossfade")
                ),
                "Transitions Complete",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error creating transitions: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private PlugInNode FindPlugin(PlugInNode root, string query)
    {
        if (root == null) return null;
        if (root.Name != null && root.Name.IndexOf(query, StringComparison.OrdinalIgnoreCase) >= 0)
        {
            if (!root.IsContainer) return root;
        }

        for (int i = 0; i < root.Count; i++)
        {
            PlugInNode child = root.GetChild(i);
            PlugInNode match = FindPlugin(child, query);
            if (match != null) return match;
        }

        return null;
    }
}
