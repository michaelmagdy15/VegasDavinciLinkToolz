using System;
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
                MessageBox.Show("No active project in VEGAS Pro.", "Clean Media Pool", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int before = vegas.Project.MediaPool.Count;
            if (before == 0)
            {
                MessageBox.Show("Project Media Pool is already empty.", "Clean Media Pool", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            DialogResult confirm = MessageBox.Show(
                string.Format("Purge all unused media from the Project Media Pool?\n\n- Currently loaded items: {0}\n- Only clips placed on the timeline will be kept.", before),
                "Confirm Purge Unused Media",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );

            if (confirm != DialogResult.Yes) return;

            vegas.Project.MediaPool.RemoveUnusedMedia();
            int after = vegas.Project.MediaPool.Count;
            int removed = before - after;

            MessageBox.Show(
                string.Format(
                    "Project Media Pool Cleaned!\n\n" +
                    "- Unused Clips Removed: {0}\n" +
                    "- Active Timeline Clips Retained: {1}\n\n" +
                    "Your .veg project file size and memory footprint have been significantly reduced.",
                    removed, after
                ),
                "Media Pool Cleaned",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error cleaning media pool: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}
