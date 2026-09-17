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
                MessageBox.Show("No active project in VEGAS Pro.", "Toggle Proxies", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int toRawCount = 0;
            int toProxyCount = 0;
            int notFoundCount = 0;

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

                if (string.IsNullOrEmpty(originalPath) || !File.Exists(originalPath))
                {
                    continue;
                }

                string ext = Path.GetExtension(originalPath).ToLower();
                if (ext == ".wav" || ext == ".mp3" || ext == ".aac" || ext == ".png" || ext == ".jpg") continue;

                string dir = Path.GetDirectoryName(originalPath);
                string fileName = Path.GetFileName(originalPath);

                // Case 1: Currently pointing to a Proxy file (e.g. ...\Proxy\file.MOV)
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
                        notFoundCount++;
                    }
                }
                // Case 2: Currently pointing to a RAW file, check if Proxy exists
                else
                {
                    string proxyCandidate = FindProxyCandidate(dir, fileName);
                    if (proxyCandidate != null && File.Exists(proxyCandidate))
                    {
                        Media targetMedia = vegas.Project.MediaPool.AddMedia(proxyCandidate);
                        media.ReplaceWith(targetMedia);
                        toProxyCount++;
                    }
                }
            }

            string msg = string.Format(
                "Proxy Toggle Complete!\n\n" +
                "- Swapped to 4K RAW (Full Res): {0} clips\n" +
                "- Swapped to Proxy (Fast Edit): {1} clips\n" +
                "- Unmatched candidates: {2}",
                toRawCount, toProxyCount, notFoundCount
            );

            MessageBox.Show(msg, "Toggle Proxies <-> RAW", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error toggling proxies: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
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

    private string FindProxyCandidate(string dir, string fileName)
    {
        string proxyDir = Path.Combine(dir, "Proxy");
        if (!Directory.Exists(proxyDir)) return null;

        string baseName = Path.GetFileNameWithoutExtension(fileName);
        string[] exts = new string[] { ".mov", ".mp4", ".m4v", ".MOV", ".MP4" };

        for (int i = 0; i < exts.Length; i++)
        {
            string cand = Path.Combine(proxyDir, baseName + exts[i]);
            if (File.Exists(cand)) return cand;
        }

        try
        {
            string[] files = Directory.GetFiles(proxyDir, baseName + ".*");
            for (int i = 0; i < files.Length; i++)
            {
                string f = files[i];
                string e = Path.GetExtension(f).ToLower();
                if (e == ".mov" || e == ".mp4" || e == ".m4v") return f;
            }
        }
        catch {}

        return null;
    }
}
