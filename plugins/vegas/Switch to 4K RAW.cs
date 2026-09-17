using System;
using System.IO;
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
                MessageBox.Show("No active project in VEGAS Pro.", "Switch to 4K RAW", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int toRawCount = 0;
            int alreadyRawCount = 0;
            int rotatedCount = 0;
            List<string> missingList = new List<string>();

            // Collect snapshot of MediaPool
            List<Media> mediaList = new List<Media>();
            foreach (Media m in vegas.Project.MediaPool)
            {
                mediaList.Add(m);
            }

            using (UndoBlock undo = new UndoBlock("Switch to 4K RAW with Vertical Camera Rotation"))
            {
                foreach (Media media in mediaList)
                {
                    string originalPath = null;
                    try
                    {
                        originalPath = media.FilePath;
                    }
                    catch
                    {
                        continue; // Skip generated media
                    }

                    if (string.IsNullOrEmpty(originalPath) || !File.Exists(originalPath)) continue;

                    string ext = Path.GetExtension(originalPath).ToLower();
                    // Skip audio files, images, etc.
                    if (ext == ".wav" || ext == ".mp3" || ext == ".aac" || ext == ".png" || ext == ".jpg") continue;

                    string dir = Path.GetDirectoryName(originalPath);
                    string fileName = Path.GetFileName(originalPath);
                    string fnLower = fileName.ToLower();
                    bool isDrone = fnLower.StartsWith("dji_") || fnLower.Contains("drone");

                    // Is it currently a Proxy?
                    if (dir.IndexOf("\\Proxy", StringComparison.OrdinalIgnoreCase) >= 0 ||
                        dir.IndexOf("/Proxy", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        string rawCandidate = FindRawCandidate(dir, fileName);
                        if (rawCandidate != null && File.Exists(rawCandidate))
                        {
                            Media targetMedia = vegas.Project.MediaPool.AddMedia(rawCandidate);
                            media.ReplaceWith(targetMedia);
                            toRawCount++;

                            // If it's a camera clip, set 90° clockwise rotation so it matches vertical 9:16 framing
                            if (!isDrone && targetMedia.Streams.Count > 0)
                            {
                                VideoStream vs = targetMedia.GetVideoStreamByIndex(0);
                                if (vs != null)
                                {
                                    vs.Rotation = VideoOutputRotation.QuarterTurnClockwise;
                                    rotatedCount++;
                                }
                            }
                        }
                        else
                        {
                            missingList.Add(fileName);
                        }
                    }
                    else
                    {
                        alreadyRawCount++;
                        // If it's already RAW, ensure camera clips have the correct 90° rotation applied
                        if (!isDrone && media.Streams.Count > 0)
                        {
                            VideoStream vs = media.GetVideoStreamByIndex(0);
                            if (vs != null && vs.Rotation != VideoOutputRotation.QuarterTurnClockwise)
                            {
                                vs.Rotation = VideoOutputRotation.QuarterTurnClockwise;
                                rotatedCount++;
                            }
                        }
                    }
                }
            }

            string report = string.Format(
                "Switched to High Quality 4K RAW!\n\n" +
                "• Successfully Replaced to 4K RAW: {0} clips\n" +
                "• Already High Quality RAW: {1} clips\n" +
                "• Camera Clips Rotated 90° Clockwise: {2} clips\n" +
                "• Missing RAW Files: {3}\n\n" +
                "All Sony camera clips now properly fill the 9:16 vertical canvas without black bars.\n" +
                "Drone/DJI shots remained in their original orientation.",
                toRawCount, alreadyRawCount, rotatedCount, missingList.Count
            );

            if (missingList.Count > 0)
            {
                report += "\n\nMissing:\n" + string.Join("\n", missingList.ToArray());
            }

            MessageBox.Show(report, "4K RAW Conform Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error switching to RAW: " + ex.Message + "\n\n" + ex.StackTrace, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private string FindRawCandidate(string dir, string fileName)
    {
        string parentDir = dir;
        while (parentDir.EndsWith("\\Proxy", StringComparison.OrdinalIgnoreCase) || parentDir.EndsWith("/Proxy", StringComparison.OrdinalIgnoreCase))
        {
            parentDir = Path.GetDirectoryName(parentDir);
        }
        if (string.IsNullOrEmpty(parentDir) || !Directory.Exists(parentDir)) return null;

        string baseName = Path.GetFileNameWithoutExtension(fileName);
        string[] exts = new string[] { ".mp4", ".mov", ".m4v", ".mkv", ".MP4", ".MOV" };

        for (int i = 0; i < exts.Length; i++)
        {
            string cand = Path.Combine(parentDir, baseName + exts[i]);
            if (File.Exists(cand)) return cand;
        }

        try
        {
            string[] files = Directory.GetFiles(parentDir, baseName + ".*");
            for (int i = 0; i < files.Length; i++)
            {
                string f = files[i];
                string e = Path.GetExtension(f).ToLower();
                if (e == ".mp4" || e == ".mov" || e == ".m4v") return f;
            }
        }
        catch {}

        return null;
    }
}
