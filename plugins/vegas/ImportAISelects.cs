using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Collections.Generic;
using ScriptPortal.Vegas;

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        try
        {
            if (vegas.Project == null)
            {
                MessageBox.Show("No active project in VEGAS Pro.", "AI Selects Importer", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            string bridgeDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".timeline_bridge");
            string manifestPath = Path.Combine(bridgeDir, "ai_selects_manifest.json");

            if (!File.Exists(manifestPath))
            {
                MessageBox.Show(
                    string.Format("Selects manifest not found:\n{0}\n\nPlease run the AI Scout first.", manifestPath),
                    "AI Selects Importer",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
                return;
            }

            string jsonText = File.ReadAllText(manifestPath, Encoding.UTF8);

            // Robust regex JSON parser for selects clips
            List<SelectClip> clips = ParseSelectsJson(jsonText);
            if (clips.Count == 0)
            {
                MessageBox.Show("No clips found in AI selects manifest.", "AI Selects Importer", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Track cache and timeline cursor positions per track
            Dictionary<string, VideoTrack> tracksByName = new Dictionary<string, VideoTrack>();
            Dictionary<string, double> trackEndMs = new Dictionary<string, double>();

            foreach (Track t in vegas.Project.Tracks)
            {
                if (t.IsVideo() && !string.IsNullOrEmpty(t.Name))
                {
                    tracksByName[t.Name] = t as VideoTrack;
                }
            }

            int importedCount = 0;

            foreach (SelectClip c in clips)
            {
                if (!File.Exists(c.MediaPath))
                {
                    continue;
                }

                Media media = Media.CreateInstance(vegas.Project, c.MediaPath);
                if (media == null)
                {
                    continue;
                }

                VideoStream vs = media.GetVideoStreamByIndex(0);
                if (vs == null)
                {
                    continue;
                }

                string targetTrackName = !string.IsNullOrEmpty(c.TrackName) ? c.TrackName : "[AI SELECTS] Kiting Action";
                VideoTrack vt = GetOrCreateTrack(vegas, tracksByName, trackEndMs, targetTrackName);

                double currentMs = trackEndMs[targetTrackName];
                Timecode start = Timecode.FromMilliseconds(currentMs);
                Timecode length = Timecode.FromMilliseconds(c.LengthMs);

                TrackEvent ev = vt.AddVideoEvent(start, length);
                Take take = ev.AddTake(vs);
                take.Offset = Timecode.FromMilliseconds(c.SourceInMs);

                // Add descriptive marker
                try
                {
                    string markerLabel = !string.IsNullOrEmpty(c.Label) ? c.Label : "[ACTION] " + Path.GetFileNameWithoutExtension(c.MediaPath);
                    Marker marker = new Marker(start, markerLabel);
                    vegas.Project.Markers.Add(marker);
                }
                catch {}

                trackEndMs[targetTrackName] = currentMs + c.LengthMs;
                importedCount++;
            }

            MessageBox.Show(
                string.Format("Successfully imported {0} AI-scouted cuts across {1} organized tracks!\n\nAll cuts are pre-trimmed to peak motion moments.", importedCount, tracksByName.Count),
                "VEGAS AI Selects",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error importing AI selects: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "AI Selects Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private VideoTrack GetOrCreateTrack(Vegas vegas, Dictionary<string, VideoTrack> tracksByName, Dictionary<string, double> trackEndMs, string trackName)
    {
        if (tracksByName.ContainsKey(trackName))
        {
            return tracksByName[trackName];
        }

        VideoTrack newTrack = new VideoTrack(vegas.Project.Tracks.Count, trackName);
        vegas.Project.Tracks.Add(newTrack);
        tracksByName[trackName] = newTrack;

        double endMs = 0.0;
        foreach (TrackEvent ev in newTrack.Events)
        {
            double evEnd = ev.End.ToMilliseconds();
            if (evEnd > endMs) endMs = evEnd;
        }
        if (endMs > 0.0) endMs += 1000.0;
        trackEndMs[trackName] = endMs;

        return newTrack;
    }

    private List<SelectClip> ParseSelectsJson(string json)
    {
        List<SelectClip> list = new List<SelectClip>();
        MatchCollection blockMatches = Regex.Matches(json, @"\{[^{}]*""media_path""[^{}]*\}", RegexOptions.Singleline);

        foreach (Match bm in blockMatches)
        {
            string block = bm.Value;
            string mediaPath = ExtractRegex(block, @"""media_path""\s*:\s*""([^""]*)""");
            string sourceInStr = ExtractRegex(block, @"""source_in_ms""\s*:\s*([0-9.]+)");
            string lengthStr = ExtractRegex(block, @"""length_ms""\s*:\s*([0-9.]+)");
            string label = ExtractRegex(block, @"""label""\s*:\s*""([^""]*)""");
            string trackName = ExtractRegex(block, @"""track_name""\s*:\s*""([^""]*)""");

            if (!string.IsNullOrEmpty(mediaPath))
            {
                double inMs = 0.0;
                double lenMs = 2500.0;
                double.TryParse(sourceInStr, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out inMs);
                double.TryParse(lengthStr, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out lenMs);

                SelectClip sc = new SelectClip();
                sc.MediaPath = mediaPath.Replace(@"\\", @"\");
                sc.SourceInMs = inMs;
                sc.LengthMs = lenMs;
                sc.Label = label;
                sc.TrackName = !string.IsNullOrEmpty(trackName) ? trackName : "[AI SELECTS] Kiting Action";
                list.Add(sc);
            }
        }
        return list;
    }

    private string ExtractRegex(string input, string pattern)
    {
        Match m = Regex.Match(input, pattern);
        if (m.Success && m.Groups.Count > 1)
        {
            return m.Groups[1].Value;
        }
        return string.Empty;
    }

    private class SelectClip
    {
        public string MediaPath;
        public double SourceInMs;
        public double LengthMs;
        public string Label;
        public string TrackName;
    }
}
