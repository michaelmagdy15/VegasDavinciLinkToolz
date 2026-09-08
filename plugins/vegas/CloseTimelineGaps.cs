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
                MessageBox.Show("No active project.", "Close Gaps", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            DialogResult res = MessageBox.Show(
                "Close all timeline gaps across all tracks?\n\n- Click YES to ripple all clips together\n- Click NO to cancel",
                "Close Timeline Gaps",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );

            if (res != DialogResult.Yes) return;

            int gapsClosed = 0;
            Timecode totalTimeSaved = Timecode.FromNanos(0);

            foreach (Track track in vegas.Project.Tracks)
            {
                if (track.Events.Count <= 1) continue;

                List<TrackEvent> sortedEvents = new List<TrackEvent>();
                foreach (TrackEvent ev in track.Events)
                {
                    sortedEvents.Add(ev);
                }

                // Sort by Start time
                sortedEvents.Sort(delegate(TrackEvent a, TrackEvent b) {
                    return a.Start.CompareTo(b.Start);
                });

                Timecode previousEnd = sortedEvents[0].End;

                for (int i = 1; i < sortedEvents.Count; i++)
                {
                    TrackEvent current = sortedEvents[i];
                    if (current.Start > previousEnd)
                    {
                        Timecode gap = current.Start - previousEnd;
                        current.Start = previousEnd;
                        previousEnd = current.End;
                        gapsClosed++;
                        totalTimeSaved = totalTimeSaved + gap;
                    }
                    else
                    {
                        if (current.End > previousEnd)
                        {
                            previousEnd = current.End;
                        }
                    }
                }
            }

            MessageBox.Show(
                string.Format("Successfully closed {0} gaps!\nTotal dead air eliminated: {1}", gapsClosed, totalTimeSaved.ToString()),
                "Gaps Closed",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error closing gaps: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}
