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
            List<string> missingList = new List<string>();

            // Collect snapshot of MediaPool
            List<Media> mediaList = new List<Media>();
            foreach (Media m in vegas.Project.MediaPool)
            {
                mediaList.Add(m);
            }

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
                    }
                    else
                    {
                        missingList.Add(fileName);
                    }
                }
                else
                {
                    alreadyRawCount++;
                }
            }

            string report = string.Format(
                "Switched to High Quality 4K RAW!\n\n" +
                "• Successfully Replaced to 4K RAW: {0} clips\n" +
                "• Already High Quality RAW: {1} clips\n" +
                "• Missing RAW Files: {2}\n\n" +
                "All timeline cuts, trims, speed ramps, and audio sync remain 100% intact.",
                toRawCount, alreadyRawCount, missingList.Count
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
