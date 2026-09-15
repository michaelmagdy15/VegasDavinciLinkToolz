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
        if (vegas.Project == null) return;
        
        // Find or create target tracks
        VideoTrack a74Track = null;
        VideoTrack djiTrack = null;
        VideoTrack rec709Track = null;
        
        foreach (Track t in vegas.Project.Tracks)
        {
            if (t.IsVideo())
            {
                string lower = (t.Name ?? "").ToLower();
                if (lower.Contains("a74 lut") || lower.Contains("a74")) a74Track = (VideoTrack)t;
                else if (lower.Contains("dji lut") || lower.Contains("dji")) djiTrack = (VideoTrack)t;
                else if (lower.Contains("rec 709") || lower.Contains("rec709")) rec709Track = (VideoTrack)t;
            }
        }
    }
}
