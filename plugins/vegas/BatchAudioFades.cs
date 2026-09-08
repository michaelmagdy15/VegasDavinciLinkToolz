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
                MessageBox.Show("No active project in VEGAS Pro.", "Batch Audio Fades", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Timecode fadeLen = Timecode.FromMilliseconds(10);
            int count = 0;

            foreach (Track track in vegas.Project.Tracks)
            {
                if (!track.IsAudio()) continue;

                foreach (TrackEvent ev in track.Events)
                {
                    if (ev is AudioEvent)
                    {
                        // Ensure event is long enough to receive 10ms fades
                        if (ev.Length.Nanos > fadeLen.Nanos * 2)
                        {
                            ev.FadeIn.Length = fadeLen;
                            ev.FadeIn.Curve = CurveType.Smooth;

                            ev.FadeOut.Length = fadeLen;
                            ev.FadeOut.Curve = CurveType.Smooth;

                            count++;
                        }
                    }
                }
            }

            MessageBox.Show(
                string.Format(
                    "Anti-Click Audio Fades Applied!\n\n" +
                    "- Audio Cuts Smoothed: {0}\n" +
                    "- Fade Length: 10ms (In & Out)\n" +
                    "- Curve: Smooth (Zero-Crossing Anti-Pop)",
                    count
                ),
                "Audio Fades Complete",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error applying audio fades: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}
