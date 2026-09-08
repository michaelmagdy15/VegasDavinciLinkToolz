/**
 * ReceiveFromResolve.cs — VEGAS Pro C# Scripting Extension
 * 
 * Round-trip bidirectional bridge: Receives timeline edits exported from DaVinci Resolve
 * and reconstructs/updates them directly on the VEGAS Pro timeline.
 * 
 * Install location:
 *   %APPDATA%\VEGAS Pro\2026.0\Script Menu\Receive from DaVinci Resolve.cs
 * (Also supports VEGAS Pro 22.0, 23.0, etc.)
 */

using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    public void FromVegas(Vegas vegas)
    {
        try
        {
            string userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            string jsonPath = Path.Combine(userProfile, ".timeline_bridge", "resolve_timeline.json");

            if (!File.Exists(jsonPath))
            {
                MessageBox.Show(
                    "No timeline found from DaVinci Resolve.\n\nPlease run 'ExportToVegas' inside DaVinci Resolve first.",
                    "VEGAS Live Link",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
                return;
            }

            string jsonContent = File.ReadAllText(jsonPath, Encoding.UTF8);

            // Simple lightweight JSON parser without external dependencies
            var manifest = SimpleJsonParser.Parse(jsonContent);

            double frameRate = manifest.ContainsKey("frame_rate") ? Convert.ToDouble(manifest["frame_rate"]) : 29.97;
            var tracks = manifest["tracks"] as List<Dictionary<string, object>>;

            if (tracks == null || tracks.Count == 0)
            {
                MessageBox.Show("No tracks found in the Resolve timeline manifest.", "VEGAS Live Link", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int clipsImported = 0;

            foreach (var trackData in tracks)
            {
                bool isVideo = trackData.ContainsKey("is_video") && Convert.ToBoolean(trackData["is_video"]);
                string trackName = trackData.ContainsKey("name") ? trackData["name"].ToString() : (isVideo ? "Video from Resolve" : "Audio from Resolve");
                var clips = trackData["clips"] as List<Dictionary<string, object>>;

                if (clips == null || clips.Count == 0) continue;

                Track vegasTrack = null;
                if (isVideo)
                {
                    vegasTrack = new VideoTrack(vegas.Project.Tracks.Count, trackName);
                }
                else
                {
                    vegasTrack = new AudioTrack(vegas.Project.Tracks.Count, trackName);
                }
                vegas.Project.Tracks.Add(vegasTrack);

                foreach (var clipData in clips)
                {
                    string mediaPath = clipData.ContainsKey("media_path") ? clipData["media_path"].ToString() : "";
                    if (string.IsNullOrEmpty(mediaPath) || !File.Exists(mediaPath)) continue;

                    double startMs = clipData.ContainsKey("timeline_start_ms") ? Convert.ToDouble(clipData["timeline_start_ms"]) : 0.0;
                    double lenMs = clipData.ContainsKey("timeline_length_ms") ? Convert.ToDouble(clipData["timeline_length_ms"]) : 0.0;
                    double inMs = clipData.ContainsKey("source_in_ms") ? Convert.ToDouble(clipData["source_in_ms"]) : 0.0;

                    Timecode startTime = Timecode.FromMilliseconds(startMs);
                    Timecode lengthTime = Timecode.FromMilliseconds(lenMs);
                    Timecode offsetTime = Timecode.FromMilliseconds(inMs);

                    Media media = Media.CreateInstance(vegas.Project, mediaPath);
                    TrackEvent trackEvent = null;

                    if (isVideo)
                    {
                        var videoTrack = vegasTrack as VideoTrack;
                        trackEvent = videoTrack.AddVideoEvent(startTime, lengthTime);
                        var videoStream = media.GetVideoStreamByIndex(0);
                        if (videoStream != null)
                        {
                            var take = trackEvent.AddTake(videoStream);
                            take.Offset = offsetTime;
                            clipsImported++;
                        }
                    }
                    else
                    {
                        var audioTrack = vegasTrack as AudioTrack;
                        trackEvent = audioTrack.AddAudioEvent(startTime, lengthTime);
                        var audioStream = media.GetAudioStreamByIndex(0);
                        if (audioStream != null)
                        {
                            var take = trackEvent.AddTake(audioStream);
                            take.Offset = offsetTime;
                            clipsImported++;
                        }
                    }
                }
            }

            MessageBox.Show(
                $"Successfully received {clipsImported} cuts from DaVinci Resolve!\nTimeline is synchronized.",
                "VEGAS Live Link",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Live Link Error: {ex.Message}", "VEGAS Live Link Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}

/// <summary>
/// Minimal pure C# JSON parser to avoid any external DLL references in VEGAS Pro script environment.
/// </summary>
public static class SimpleJsonParser
{
    public static Dictionary<string, object> Parse(string json)
    {
        var result = new Dictionary<string, object>();
        json = json.Trim();
        if (!json.StartsWith("{") || !json.EndsWith("}")) return result;

        // Extract frame_rate
        var frIdx = json.IndexOf("\"frame_rate\":");
        if (frIdx >= 0)
        {
            int start = frIdx + 13;
            int end = json.IndexOfAny(new char[] { ',', '\r', '\n', '}' }, start);
            if (end > start)
            {
                double val;
                if (double.TryParse(json.Substring(start, end - start).Trim(), System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out val))
                {
                    result["frame_rate"] = val;
                }
            }
        }

        // Extract tracks
        var tracksList = new List<Dictionary<string, object>>();
        var trIdx = json.IndexOf("\"tracks\":");
        if (trIdx >= 0)
        {
            int arrayStart = json.IndexOf('[', trIdx);
            int arrayEnd = json.LastIndexOf(']');
            if (arrayStart >= 0 && arrayEnd > arrayStart)
            {
                string tracksArrayStr = json.Substring(arrayStart + 1, arrayEnd - arrayStart - 1);
                var trackBlocks = SplitObjects(tracksArrayStr);
                foreach (var tb in trackBlocks)
                {
                    var trackDict = new Dictionary<string, object>();
                    trackDict["is_video"] = tb.Contains("\"is_video\": true");
                    trackDict["is_audio"] = tb.Contains("\"is_audio\": true");

                    var nameMatch = ExtractStringProp(tb, "name");
                    trackDict["name"] = nameMatch;

                    var clipsList = new List<Dictionary<string, object>>();
                    int clipsStart = tb.IndexOf("\"clips\":");
                    if (clipsStart >= 0)
                    {
                        int cStart = tb.IndexOf('[', clipsStart);
                        int cEnd = tb.IndexOf(']', cStart);
                        if (cStart >= 0 && cEnd > cStart)
                        {
                            string clipsArrayStr = tb.Substring(cStart + 1, cEnd - cStart - 1);
                            var clipBlocks = SplitObjects(clipsArrayStr);
                            foreach (var cb in clipBlocks)
                            {
                                var clipDict = new Dictionary<string, object>();
                                clipDict["name"] = ExtractStringProp(cb, "name");
                                clipDict["media_path"] = ExtractStringProp(cb, "media_path");
                                clipDict["timeline_start_ms"] = ExtractDoubleProp(cb, "timeline_start_ms");
                                clipDict["timeline_length_ms"] = ExtractDoubleProp(cb, "timeline_length_ms");
                                clipDict["source_in_ms"] = ExtractDoubleProp(cb, "source_in_ms");
                                clipsList.Add(clipDict);
                            }
                        }
                    }
                    trackDict["clips"] = clipsList;
                    tracksList.Add(trackDict);
                }
            }
        }
        result["tracks"] = tracksList;
        return result;
    }

    private static string ExtractStringProp(string block, string prop)
    {
        string pattern = "\"" + prop + "\": \"";
        int idx = block.IndexOf(pattern);
        if (idx < 0) return "";
        int start = idx + pattern.Length;
        int end = block.IndexOf("\"", start);
        if (end < 0) return "";
        return block.Substring(start, end - start).Replace("\\\\", "\\");
    }

    private static double ExtractDoubleProp(string block, string prop)
    {
        string pattern = "\"" + prop + "\":";
        int idx = block.IndexOf(pattern);
        if (idx < 0) return 0.0;
        int start = idx + pattern.Length;
        int end = block.IndexOfAny(new char[] { ',', '\r', '\n', '}' }, start);
        if (end < 0) return 0.0;
        double val;
        if (double.TryParse(block.Substring(start, end - start).Trim(), System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out val))
            return val;
        return 0.0;
    }

    private static List<string> SplitObjects(string arrayContent)
    {
        var list = new List<string>();
        int depth = 0;
        int start = -1;
        for (int i = 0; i < arrayContent.Length; i++)
        {
            if (arrayContent[i] == '{')
            {
                if (depth == 0) start = i;
                depth++;
            }
            else if (arrayContent[i] == '}')
            {
                depth--;
                if (depth == 0 && start >= 0)
                {
                    list.Add(arrayContent.Substring(start, i - start + 1));
                    start = -1;
                }
            }
        }
        return list;
    }
}
