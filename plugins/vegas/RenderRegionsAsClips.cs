using System;
using System.IO;
using System.Text.RegularExpressions;
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
                MessageBox.Show("No active project in VEGAS Pro.", "Render Regions", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int regionCount = vegas.Project.Regions.Count;
            if (regionCount == 0)
            {
                MessageBox.Show(
                    "No timeline regions found.\n\nTo use Batch Region Render, mark sections of your timeline with Regions (shortcut key 'R' in VEGAS).",
                    "No Regions Found",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
                return;
            }

            // Find best video renderer & template
            Renderer chosenRenderer = null;
            RenderTemplate chosenTemplate = null;

            foreach (Renderer r in vegas.Renderers)
            {
                string rName = (r.Name ?? "").ToLower();
                if (rName.Contains("magix avc") || rName.Contains("sony avc") || rName.Contains("mp4") || rName.Contains("prores"))
                {
                    foreach (RenderTemplate t in r.Templates)
                    {
                        if (t.IsValid())
                        {
                            chosenRenderer = r;
                            chosenTemplate = t;
                            break;
                        }
                    }
                }
                if (chosenTemplate != null) break;
            }

            if (chosenRenderer == null || chosenTemplate == null)
            {
                // Fallback to first valid renderer with templates
                foreach (Renderer r in vegas.Renderers)
                {
                    if (r.SupportsVideo)
                    {
                        foreach (RenderTemplate t in r.Templates)
                        {
                            if (t.IsValid())
                            {
                                chosenRenderer = r;
                                chosenTemplate = t;
                                break;
                            }
                        }
                    }
                    if (chosenTemplate != null) break;
                }
            }

            if (chosenRenderer == null || chosenTemplate == null)
            {
                MessageBox.Show("No suitable video render template found.", "Render Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            // Choose output folder
            string exportDir = "";
            using (FolderBrowserDialog fbd = new FolderBrowserDialog())
            {
                fbd.Description = string.Format("Select Destination Folder for {0} Region Clips", regionCount);
                if (fbd.ShowDialog() != DialogResult.OK || string.IsNullOrEmpty(fbd.SelectedPath))
                {
                    return;
                }
                exportDir = fbd.SelectedPath;
            }

            string ext = chosenRenderer.FileExtension ?? ".mp4";
            if (!ext.StartsWith(".")) ext = "." + ext;

            int renderedCount = 0;
            int failedCount = 0;

            for (int i = 0; i < vegas.Project.Regions.Count; i++)
            {
                Region reg = vegas.Project.Regions[i];
                string label = reg.Label;
                if (string.IsNullOrEmpty(label)) label = string.Format("Region_{0:D2}", i + 1);

                // Sanitize filename
                string safeName = Regex.Replace(label, @"[\\/:*?""<>|]", "_").Trim();
                string outPath = Path.Combine(exportDir, safeName + ext);

                // Avoid collision
                int dupe = 1;
                while (File.Exists(outPath))
                {
                    outPath = Path.Combine(exportDir, string.Format("{0}_{1}{2}", safeName, dupe, ext));
                    dupe++;
                }

                RenderArgs args = new RenderArgs();
                args.OutputFile = outPath;
                args.RenderTemplate = chosenTemplate;
                args.Start = reg.Position;
                args.Length = reg.Length;

                RenderStatus status = vegas.Render(args);
                if (status == RenderStatus.Complete)
                {
                    renderedCount++;
                }
                else if (status == RenderStatus.Canceled)
                {
                    MessageBox.Show("Batch render was canceled by user.", "Render Canceled", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    break;
                }
                else
                {
                    failedCount++;
                }
            }

            MessageBox.Show(
                string.Format(
                    "Batch Region Render Complete!\n\n" +
                    "- Successfully Rendered: {0} clips\n" +
                    "- Failed: {1}\n" +
                    "- Destination: {2}\n" +
                    "- Template: {3} ({4})",
                    renderedCount, failedCount, exportDir, chosenRenderer.Name, chosenTemplate.Name
                ),
                "Render Complete",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error rendering regions: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}
