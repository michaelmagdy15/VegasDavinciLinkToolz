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
                MessageBox.Show("No active project in VEGAS Pro.", "Impact Snap Zoom", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            List<VideoEvent> targetEvents = new List<VideoEvent>();

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

            if (targetEvents.Count == 0)
            {
                MessageBox.Show(
                    "Please select one or more video clips where you want the Impact Snap-Zoom (Hit Punch) applied.",
                    "No Clips Selected",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
                return;
            }

            int count = 0;
            // 6 frames punch duration (approx 0.10s at 60fps, 0.20s at 24/30fps)
            Timecode snapDuration = Timecode.FromFrames(6);

            foreach (VideoEvent vEvent in targetEvents)
            {
                VideoMotion motion = vEvent.VideoMotion;
                if (motion.Keyframes.Count == 0) continue;

                VideoMotionKeyframe kf0 = motion.Keyframes[0];
                VideoMotionBounds origBounds = kf0.Bounds;

                // Punch in: shrink crop box by 12% -> zooms video in by ~14%
                kf0.ScaleBy(new VideoMotionVertex(0.88f, 0.88f));
                kf0.Smoothness = 0.8f;

                // Return to normal frame after 6 frames
                if (snapDuration < vEvent.Length)
                {
                    VideoMotionKeyframe kf1 = new VideoMotionKeyframe(snapDuration);
                    motion.Keyframes.Add(kf1);
                    kf1.Bounds = origBounds;
                    kf1.Smoothness = 0.8f;
                }

                count++;
            }

            MessageBox.Show(
                string.Format("Successfully applied Impact Snap-Zoom punch to {0} clip(s)!\n\nPunch scale: 114% zoom-in -> Snaps back to 100% over 6 frames.", count),
                "Impact Snap Zoom",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error applying snap zoom: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}
