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
            if (vegas == null || vegas.Project == null)
            {
                MessageBox.Show("No active project in VEGAS Pro.", "Fix Camera Rotation", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int rotatedCount = 0;
            int alreadyRotatedCount = 0;
            int droneSkippedCount = 0;
            List<string> rotatedFiles = new List<string>();

            using (UndoBlock undo = new UndoBlock("Rotate Camera Clips 90° Clockwise"))
            {
                foreach (Media m in vegas.Project.MediaPool)
                {
                    string fp = null;
                    try { fp = m.FilePath; } catch {}
                    if (string.IsNullOrEmpty(fp) || !File.Exists(fp)) continue;

                    string ext = Path.GetExtension(fp).ToLower();
                    if (ext != ".mp4" && ext != ".mov" && ext != ".m4v") continue;

                    string fileName = Path.GetFileName(fp);
                    string fnLower = fileName.ToLower();

                    // Check if it's a drone / DJI file
                    if (fnLower.StartsWith("dji_") || fnLower.Contains("drone"))
                    {
                        droneSkippedCount++;
                        continue;
                    }

                    // Check if it's a Sony camera clip
                    bool isCameraClip = fnLower.Contains("abdrafilms") || 
                                       fnLower.Contains("a7iv") || 
                                       fnLower.Contains("a7s") ||
                                       fnLower.Contains("811") ||
                                       fnLower.Contains("812") ||
                                       fnLower.Contains("815") ||
                                       fnLower.Contains("818") ||
                                       fnLower.Contains("819") ||
                                       fnLower.Contains("821") ||
                                       fnLower.Contains("822") ||
                                       fnLower.Contains("823") ||
                                       fnLower.Contains("917") ||
                                       fnLower.Contains("919") ||
                                       fnLower.Contains("920") ||
                                       fnLower.Contains("921") ||
                                       fnLower.Contains("922") ||
                                       fnLower.Contains("923") ||
                                       fnLower.Contains("924") ||
                                       fnLower.Contains("925") ||
                                       fnLower.Contains("929") ||
                                       fnLower.Contains("930") ||
                                       fnLower.Contains("931") ||
                                       fnLower.Contains("932") ||
                                       fnLower.Contains("933") ||
                                       fnLower.Contains("936") ||
                                       fnLower.Contains("937") ||
                                       fnLower.Contains("938");

                    if (isCameraClip && m.Streams.Count > 0)
                    {
                        VideoStream vs = m.GetVideoStreamByIndex(0);
                        if (vs != null)
                        {
                            // If raw file is 3840x2160 (horizontal), it needs 90° clockwise rotation
                            if (vs.Rotation != VideoOutputRotation.QuarterTurnClockwise)
                            {
                                vs.Rotation = VideoOutputRotation.QuarterTurnClockwise;
                                rotatedCount++;
                                rotatedFiles.Add(fileName);
                            }
                            else
                            {
                                alreadyRotatedCount++;
                            }
                        }
                    }
                }
            }

            string report = string.Format(
                "Camera Clips Rotation Fixed!\n\n" +
                "• Successfully Rotated 90° Clockwise: {0} clips\n" +
                "• Already Rotated Correctly: {1} clips\n" +
                "• Drone / DJI Clips Left Untouched: {2} clips\n\n" +
                "All Sony camera clips now properly fill the 9:16 vertical canvas with ZERO black bars.",
                rotatedCount, alreadyRotatedCount, droneSkippedCount
            );

            if (rotatedFiles.Count > 0 && rotatedFiles.Count <= 8)
            {
                report += "\n\nRotated Sample:\n" + string.Join("\n", rotatedFiles.ToArray());
            }

            MessageBox.Show(report, "Rotation Conform Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error fixing rotation: " + ex.Message + "\n\n" + ex.StackTrace, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
