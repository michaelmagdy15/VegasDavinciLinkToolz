using System;
using System.IO;
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

            // Collect media items
            foreach (Media media in vegas.Project.MediaPool)
            {
                string originalPath = media.FilePath;
                if (string.IsNullOrEmpty(originalPath) || !File.Exists(originalPath))
                {
                    continue;
                }

                string dir = Path.GetDirectoryName(originalPath);
                string fileName = Path.GetFileName(originalPath);

                // Case 1: Currently pointing to a Proxy file (e.g. ...\Proxy\file.MOV)
                if (dir.EndsWith("\\Proxy", StringComparison.OrdinalIgnoreCase) ||
                    dir.EndsWith("/Proxy", StringComparison.OrdinalIgnoreCase))
                {
                    string parentDir = Path.GetDirectoryName(dir);
                    string rawCandidate = Path.Combine(parentDir, fileName);

                    // Check exact or common extensions
                    if (File.Exists(rawCandidate))
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
                    string proxyCandidate = Path.Combine(dir, "Proxy", fileName);
                    if (File.Exists(proxyCandidate))
                    {
                        Media targetMedia = vegas.Project.MediaPool.AddMedia(proxyCandidate);
                        media.ReplaceWith(targetMedia);
                        toProxyCount++;
                    }
                }
            }

            string msg = string.Format(
                "Proxy Toggle Complete!\n\n" +
                "- Swapped to RAW (Full Res): {0} clips\n" +
                "- Swapped to Proxy (Fast Edit): {1} clips\n" +
                "- Missing RAW candidates: {2}",
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
}
