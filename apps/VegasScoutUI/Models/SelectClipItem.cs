using System;

namespace VegasScoutUI.Models;

public class SelectClipItem
{
    public string Name { get; set; } = string.Empty;
    public string MediaPath { get; set; } = string.Empty;
    public double SourceInMs { get; set; }
    public double LengthMs { get; set; }
    public double Score { get; set; }
    public string Label { get; set; } = string.Empty;
    public string TrackName { get; set; } = string.Empty;

    public string FormattedIn
    {
        get
        {
            TimeSpan ts = TimeSpan.FromMilliseconds(SourceInMs);
            return string.Format("{0:D2}:{1:D2}:{2:D2}.{3:D1}", ts.Hours, ts.Minutes, ts.Seconds, ts.Milliseconds / 100);
        }
    }

    public string FormattedDuration => string.Format("{0:0.1}s", LengthMs / 1000.0);

    public string FormattedScore => string.Format("{0:P0} Action", Score);

    public string ScoreBadgeBackground
    {
        get
        {
            if (Score >= 0.7) return "#22C55E"; // Emerald Green
            if (Score >= 0.4) return "#3B82F6"; // Blue
            return "#F59E0B"; // Amber
        }
    }
}
