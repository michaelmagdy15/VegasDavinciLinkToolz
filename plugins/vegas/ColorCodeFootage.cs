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
                MessageBox.Show("No active project in VEGAS Pro.", "Color Code Footage", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int slowMoCount = 0;
            int actionCount = 0;
            int cinemaCount = 0;

            foreach (Track track in vegas.Project.Tracks)
            {
                if (!track.IsVideo()) continue;

                int trackSlowMo = 0;
                int trackAction = 0;
                int trackCinema = 0;

                foreach (TrackEvent ev in track.Events)
                {
                    if (!(ev is VideoEvent)) continue;
                    VideoEvent vEvent = (VideoEvent)ev;
                    Take take = vEvent.ActiveTake;
                    if (take == null) continue;

                    VideoStream vStream = take.MediaStream as VideoStream;
                    if (vStream == null && take.Media != null && take.Media.HasVideo())
                    {
                        try { vStream = take.Media.GetVideoStreamByIndex(0); } catch {}
                    }

                    if (vStream == null) continue;

                    double fps = vStream.FrameRate;
                    string baseName = CleanOldTags(take.Name);

                    if (fps >= 90.0)
                    {
                        take.Name = string.Format("[120fps SLOW-MO] {0}", baseName);
                        slowMoCount++;
                        trackSlowMo++;
                    }
                    else if (fps >= 48.0)
                    {
                        take.Name = string.Format("[60fps ACTION] {0}", baseName);
                        actionCount++;
                        trackAction++;
                    }
                    else
                    {
                        take.Name = string.Format("[24fps CINEMA] {0}", baseName);
                        cinemaCount++;
                        trackCinema++;
                    }
                }

                // Update track name with dominant footage profile
                string cleanTrackName = CleanTrackTags(track.Name);
                if (trackSlowMo > trackAction && trackSlowMo > trackCinema)
                {
                    track.Name = string.Format("[SLOW-MO 120fps] {0}", cleanTrackName);
                }
                else if (trackAction > trackCinema)
                {
                    track.Name = string.Format("[ACTION 60fps] {0}", cleanTrackName);
                }
                else if (trackCinema > 0 && string.IsNullOrEmpty(cleanTrackName))
                {
                    track.Name = string.Format("[CINEMA 24fps] {0}", cleanTrackName);
                }
            }

            string report = string.Format(
                "Footage Classified & Tagged Successfully!\n\n" +
                "- 🟣 100fps / 120fps (Slow-Mo Ready): {0} clips\n" +
                "- 🟢 50fps / 60fps (Sports & Action): {1} clips\n" +
                "- 🔵 24fps / 25fps / 30fps (Cinematic): {2} clips\n\n" +
                "Track header colors and take labels updated.",
                slowMoCount, actionCount, cinemaCount
            );

            MessageBox.Show(report, "Footage Tagged by Frame Rate", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error tagging footage: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private string CleanOldTags(string name)
    {
        if (string.IsNullOrEmpty(name)) return "";
        string clean = name;
        string[] prefixes = new string[] {
            "[120fps SLOW-MO] ", "[60fps ACTION] ", "[24fps CINEMA] ",
            "[120fps] ", "[60fps] ", "[24fps] "
        };
        foreach (string p in prefixes)
        {
            if (clean.StartsWith(p)) clean = clean.Substring(p.Length);
        }
        return clean.Trim();
    }

    private string CleanTrackTags(string name)
    {
        if (string.IsNullOrEmpty(name)) return "";
        string clean = name;
        string[] prefixes = new string[] {
            "[SLOW-MO 120fps] ", "[ACTION 60fps] ", "[CINEMA 24fps] "
        };
        foreach (string p in prefixes)
        {
            if (clean.StartsWith(p)) clean = clean.Substring(p.Length);
        }
        return clean.Trim();
    }
}
