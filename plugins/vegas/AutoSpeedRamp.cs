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
                MessageBox.Show("No active project in VEGAS Pro.", "Auto Speed Ramp", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            List<VideoEvent> targetEvents = new List<VideoEvent>();

            // Find selected video events
            foreach (Track track in vegas.Project.Tracks)
            {
                if (!track.IsVideo()) continue;

                foreach (TrackEvent ev in track.Events)
                {
                    if (ev.Selected && ev is VideoEvent)
                    {
                        targetEvents.Add((VideoEvent)ev);
                    }
                }
            }

            // If none selected, offer to apply to the first clip under cursor or prompt
            if (targetEvents.Count == 0)
            {
                DialogResult prompt = MessageBox.Show(
                    "No video events are currently selected.\n\nWould you like to apply the Action Speed Ramp to ALL events on the active video track?",
                    "Select Events",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question
                );

                if (prompt != DialogResult.Yes) return;

                foreach (Track track in vegas.Project.Tracks)
                {
                    if (track.IsVideo() && track.Selected)
                    {
                        foreach (TrackEvent ev in track.Events)
                        {
                            if (ev is VideoEvent) targetEvents.Add((VideoEvent)ev);
                        }
                    }
                }

                if (targetEvents.Count == 0)
                {
                    MessageBox.Show("Please select a video track or select specific clips first.", "Auto Speed Ramp", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }
            }

            int count = 0;
            foreach (VideoEvent vEvent in targetEvents)
            {
                if (!vEvent.CanAddEnvelope(EnvelopeType.Velocity)) continue;

                Envelope velocityEnv = null;
                if (vEvent.Envelopes.HasEnvelope(EnvelopeType.Velocity))
                {
                    velocityEnv = vEvent.Envelopes.FindByType(EnvelopeType.Velocity);
                    velocityEnv.Points.Clear();
                }
                else
                {
                    velocityEnv = new Envelope(EnvelopeType.Velocity);
                    vEvent.Envelopes.Add(velocityEnv);
                }

                long totalNanos = vEvent.Length.Nanos;

                // Action Ramp Timing:
                // 0.00s : 3.0x (300% hyper-speed entry)
                // 25%   : 3.0x (maintains approach)
                // 35%   : 0.4x (smooth plunge into slow-mo)
                // 70%   : 0.4x (slow-mo trick peak)
                // 85%   : 1.0x (resumes normal speed for landing)
                Timecode t0 = Timecode.FromNanos(0);
                Timecode t1 = Timecode.FromNanos((long)(totalNanos * 0.25));
                Timecode t2 = Timecode.FromNanos((long)(totalNanos * 0.35));
                Timecode t3 = Timecode.FromNanos((long)(totalNanos * 0.70));
                Timecode t4 = Timecode.FromNanos((long)(totalNanos * 0.85));

                velocityEnv.Points.Add(new EnvelopePoint(t0, 3.0, CurveType.Linear));
                velocityEnv.Points.Add(new EnvelopePoint(t1, 3.0, CurveType.Smooth));
                velocityEnv.Points.Add(new EnvelopePoint(t2, 0.4, CurveType.Smooth));
                velocityEnv.Points.Add(new EnvelopePoint(t3, 0.4, CurveType.Smooth));
                velocityEnv.Points.Add(new EnvelopePoint(t4, 1.0, CurveType.Smooth));

                // Enable smooth frame resampling
                try
                {
                    vEvent.ResampleMode = VideoResampleMode.Smart;
                }
                catch {}

                count++;
            }

            MessageBox.Show(
                string.Format("Successfully generated Action Speed Ramps on {0} clip(s)!\n\nCurve applied: 300% Approach -> 40% Peak Trick Slow-Mo -> 100% Landing.", count),
                "Speed Ramp Complete",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error applying speed ramp: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}
