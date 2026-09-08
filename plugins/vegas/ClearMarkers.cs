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
                MessageBox.Show("No active project in VEGAS Pro.", "Clear Markers", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int count = vegas.Project.Markers.Count;
            int regionsCount = vegas.Project.Regions.Count;

            if (count == 0 && regionsCount == 0)
            {
                MessageBox.Show("There are no markers or regions on the timeline to remove.", "Clear Markers", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            DialogResult confirm = MessageBox.Show(
                string.Format("Are you sure you want to remove all {0} markers and {1} regions from the timeline?", count, regionsCount),
                "Confirm Remove All Markers",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );

            if (confirm != DialogResult.Yes)
            {
                return;
            }

            // Remove all markers
            List<Marker> markerList = new List<Marker>();
            foreach (Marker m in vegas.Project.Markers)
            {
                markerList.Add(m);
            }
            foreach (Marker m in markerList)
            {
                try { vegas.Project.Markers.Remove(m); } catch {}
            }

            // Remove all regions if any
            List<Region> regionList = new List<Region>();
            foreach (Region r in vegas.Project.Regions)
            {
                regionList.Add(r);
            }
            foreach (Region r in regionList)
            {
                try { vegas.Project.Regions.Remove(r); } catch {}
            }

            MessageBox.Show(
                string.Format("Successfully removed {0} markers and {1} regions from the timeline!", count, regionsCount),
                "Markers Cleared",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error clearing markers: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }
}
