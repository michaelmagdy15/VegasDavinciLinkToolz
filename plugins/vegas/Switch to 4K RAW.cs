using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Windows.Forms;
using ScriptPortal.Vegas;

public class EntryPoint
{
    // Cache raw Media objects to avoid duplicate MediaPool entries
    private Dictionary<string, Media> rawMediaCache = new Dictionary<string, Media>(StringComparer.OrdinalIgnoreCase);
    private StringBuilder diagLog = new StringBuilder();

    public void FromVegas(Vegas vegas)
    {
        try
        {
            if (vegas.Project == null)
            {
                MessageBox.Show("No active project in VEGAS Pro.", "Switch to 4K RAW", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Project proj = vegas.Project;
            int switchedVideoCount = 0;
            int switchedAudioCount = 0;
            int alreadyRawCount = 0;
            int skippedCount = 0;
            List<string> missingList = new List<string>();
            List<string> errorList = new List<string>();

            diagLog.AppendLine("=== Switch to 4K RAW — Diagnostic Log ===");
            diagLog.AppendLine("Timestamp: " + DateTime.Now.ToString("o"));
            diagLog.AppendLine("Project: " + (proj.FilePath ?? "Untitled"));
            diagLog.AppendLine();

            using (UndoBlock undo = new UndoBlock("Switch Proxy → 4K RAW"))
            {
                foreach (Track track in proj.Tracks)
                {
                    string trackName = track.Name ?? "";
                    string tnameLower = trackName.ToLower();
                    bool isVideo = track.IsVideo();
                    bool isAudio = track.IsAudio();

                    // Skip adjustment / overlay / transition tracks
                    if (isVideo)
                    {
                        VideoTrack vt = track as VideoTrack;
                        if (vt != null && vt.IsAdjustmentTrack) continue;
                        if (tnameLower.Contains("[adjustment]") ||
                            tnameLower.Contains("film burn") ||
                            tnameLower.Contains("filmburn") ||
                            tnameLower.Contains("halation") ||
                            tnameLower.Contains("transiotions") ||
                            tnameLower.Contains("transition"))
                        {
                            continue;
                        }
                    }

                    foreach (TrackEvent ev in track.Events)
                    {
                        Take activeTake = ev.ActiveTake;
                        if (activeTake == null || activeTake.Media == null) continue;

                        // Skip events already replaced by AutoReplaceClientShots
                        string takeName = activeTake.Name ?? "";
                        if (takeName.Contains("[REPLACED]")) continue;

                        // Get media path — use same fallback chain as DeepScan
                        string mediaPath = "";
                        try
                        {
                            mediaPath = activeTake.MediaPath ?? "";
                            if (string.IsNullOrEmpty(mediaPath) || !File.Exists(mediaPath))
                            {
                                mediaPath = activeTake.Media.FilePath ?? "";
                            }
                        }
                        catch
                        {
                            continue;
                        }

                        if (string.IsNullOrEmpty(mediaPath)) continue;

                        string ext = Path.GetExtension(mediaPath).ToLower();

                        // Skip non-video/audio media (images, etc.)
                        if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" ||
                            ext == ".bmp" || ext == ".tif" || ext == ".tiff" ||
                            ext == ".gif")
                        {
                            continue;
                        }

                        // Skip standalone audio files (not embedded in proxy video)
                        if (ext == ".wav" || ext == ".mp3" || ext == ".aac" ||
                            ext == ".flac" || ext == ".ogg")
                        {
                            continue;
                        }

                        string dir = "";
                        string fileName = "";
                        string baseName = "";
                        try
                        {
                            dir = Path.GetDirectoryName(mediaPath) ?? "";
                            fileName = Path.GetFileName(mediaPath);
                            baseName = Path.GetFileNameWithoutExtension(mediaPath);
                        }
                        catch
                        {
                            continue;
                        }

                        // ——————————————————————————————————————————
                        // PROXY DETECTION — Two strategies
                        // ——————————————————————————————————————————
                        bool isProxy = false;
                        string rawCandidate = null;

                        // Strategy 1: Directory path contains \Proxy
                        if (IsProxyDirectory(dir))
                        {
                            isProxy = true;
                            rawCandidate = FindRawFromProxyDir(dir, baseName);
                            diagLog.AppendLine("[PROXY-DIR] " + fileName);
                            diagLog.AppendLine("  Media:  " + mediaPath);
                            diagLog.AppendLine("  RawDir: " + GetParentOfProxy(dir));
                            diagLog.AppendLine("  Raw:    " + (rawCandidate ?? "NOT FOUND"));
                        }
                        // Strategy 2: .mov file where a matching .mp4 exists in same or parent dir
                        // (handles cases where proxy detection by folder name fails)
                        else if (ext == ".mov")
                        {
                            rawCandidate = FindRawMp4Sibling(dir, baseName);
                            if (rawCandidate != null)
                            {
                                isProxy = true;
                                diagLog.AppendLine("[PROXY-EXT] " + fileName);
                                diagLog.AppendLine("  Media: " + mediaPath);
                                diagLog.AppendLine("  Raw:   " + rawCandidate);
                            }
                        }

                        if (!isProxy)
                        {
                            alreadyRawCount++;
                            continue;
                        }

                        if (rawCandidate == null || !File.Exists(rawCandidate))
                        {
                            missingList.Add(fileName + " → expected: " + (rawCandidate ?? "?"));
                            diagLog.AppendLine("  ❌ RAW FILE NOT FOUND");
                            continue;
                        }

                        // ——————————————————————————————————————————
                        // Check if event already has a take pointing to the raw file
                        // ——————————————————————————————————————————
                        bool alreadyHasRawTake = false;
                        foreach (Take tk in ev.Takes)
                        {
                            try
                            {
                                string tkPath = tk.MediaPath ?? "";
                                if (string.IsNullOrEmpty(tkPath) && tk.Media != null)
                                    tkPath = tk.Media.FilePath ?? "";

                                if (!string.IsNullOrEmpty(tkPath) &&
                                    tkPath.Equals(rawCandidate, StringComparison.OrdinalIgnoreCase))
                                {
                                    ev.ActiveTake = tk;
                                    alreadyHasRawTake = true;
                                    if (isVideo)
                                    {
                                        switchedVideoCount++;
                                        VideoEvent ve = ev as VideoEvent;
                                        if (ve != null && tk.Media != null && tk.Media.Streams.Count > 0)
                                        {
                                            ConformPanCropForRaw(ve, tk.Media.GetVideoStreamByIndex(0));
                                        }
                                    }
                                    else if (isAudio) switchedAudioCount++;
                                    diagLog.AppendLine("  ✓ Activated existing RAW take (Pan/Crop conformed)");
                                    break;
                                }
                            }
                            catch { }
                        }

                        if (alreadyHasRawTake) continue;

                        // ——————————————————————————————————————————
                        // Get or add the raw Media to the pool
                        // ——————————————————————————————————————————
                        Media rawMedia = GetOrAddMedia(proj, rawCandidate);
                        if (rawMedia == null)
                        {
                            errorList.Add("Failed to load media: " + Path.GetFileName(rawCandidate));
                            diagLog.AppendLine("  ❌ Failed to add media to pool");
                            continue;
                        }

                        // ——————————————————————————————————————————
                        // VIDEO EVENT: Add raw video take
                        // ——————————————————————————————————————————
                        if (isVideo)
                        {
                            VideoEvent ve = ev as VideoEvent;
                            if (ve == null) continue;

                            VideoStream rawVideoStream = rawMedia.GetVideoStreamByIndex(0);
                            if (rawVideoStream == null)
                            {
                                errorList.Add("No video stream in: " + Path.GetFileName(rawCandidate));
                                diagLog.AppendLine("  ❌ No video stream");
                                continue;
                            }

                            // Preserve the current take offset (keeps trim/in-point intact)
                            Timecode originalOffset = activeTake.Offset;

                            // Add new take with raw video stream
                            Take rawTake = ve.AddTake(rawVideoStream);
                            rawTake.Offset = originalOffset;
                            rawTake.Name = "4K RAW: " + Path.GetFileName(rawCandidate);
                            ve.ActiveTake = rawTake;
                            ConformPanCropForRaw(ve, rawVideoStream);
                            switchedVideoCount++;

                            diagLog.AppendLine("  ✓ Video SWITCHED (Pan/Crop conformed)");
                        }
                        // ——————————————————————————————————————————
                        // AUDIO EVENT: Add raw audio take (for embedded audio in proxy)
                        // ——————————————————————————————————————————
                        else if (isAudio)
                        {
                            AudioStream rawAudioStream = rawMedia.GetAudioStreamByIndex(0);
                            if (rawAudioStream == null)
                            {
                                // No audio stream in raw file — not an error, some raw files have separate audio
                                skippedCount++;
                                diagLog.AppendLine("  ⚠ No audio stream in raw (separate audio likely)");
                                continue;
                            }

                            Timecode originalOffset = activeTake.Offset;

                            Take rawAudioTake = ev.AddTake(rawAudioStream);
                            rawAudioTake.Offset = originalOffset;
                            rawAudioTake.Name = "4K RAW Audio: " + Path.GetFileName(rawCandidate);
                            ev.ActiveTake = rawAudioTake;
                            switchedAudioCount++;

                            diagLog.AppendLine("  ✓ Audio SWITCHED");
                        }
                    }
                }
            }

            // Save diagnostic log
            string logDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".timeline_bridge");
            if (!Directory.Exists(logDir)) Directory.CreateDirectory(logDir);
            string logPath = Path.Combine(logDir, "proxy_switch_log.txt");

            diagLog.AppendLine();
            diagLog.AppendLine("=== SUMMARY ===");
            diagLog.AppendLine("Video events switched: " + switchedVideoCount);
            diagLog.AppendLine("Audio events switched: " + switchedAudioCount);
            diagLog.AppendLine("Already RAW: " + alreadyRawCount);
            diagLog.AppendLine("Missing RAW: " + missingList.Count);
            diagLog.AppendLine("Errors: " + errorList.Count);

            File.WriteAllText(logPath, diagLog.ToString(), new UTF8Encoding(false));

            // Summary report
            string report = string.Format(
                "Switched to 4K RAW!\n\n" +
                "• Video Events Switched to 4K RAW: {0}\n" +
                "• Audio Events Switched to 4K RAW: {1}\n" +
                "• Already 4K RAW (no change): {2}\n" +
                "• Missing RAW Files: {3}\n" +
                "• Errors: {4}\n\n" +
                "All timeline cuts, trims, speed ramps, and positions are 100% intact.\n" +
                "Press 'T' on any event to toggle between proxy and RAW takes.\n\n" +
                "Diagnostic log:\n{5}",
                switchedVideoCount, switchedAudioCount, alreadyRawCount,
                missingList.Count, errorList.Count, logPath
            );

            if (missingList.Count > 0)
            {
                report += "\n\nMissing RAW files:\n• " + string.Join("\n• ", missingList.ToArray());
            }

            if (errorList.Count > 0)
            {
                report += "\n\nErrors:\n• " + string.Join("\n• ", errorList.ToArray());
            }

            MessageBox.Show(report, "4K RAW Conform Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                "Error switching to RAW:\n" + ex.Message + "\n\n" + ex.StackTrace,
                "Error", MessageBoxButtons.OK, MessageBoxIcon.Error
            );
        }
    }

    // ——————————————————————————————————————————————————————
    // Proxy Detection
    // ——————————————————————————————————————————————————————

    /// <summary>
    /// Check if a directory path indicates a Proxy folder.
    /// Matches: ...\Proxy, ...\Proxy\..., .../Proxy, .../Proxy/...
    /// </summary>
    private bool IsProxyDirectory(string dir)
    {
        if (string.IsNullOrEmpty(dir)) return false;

        // Check if the directory itself IS named "Proxy"
        string dirName = Path.GetFileName(dir);
        if (string.Equals(dirName, "Proxy", StringComparison.OrdinalIgnoreCase))
            return true;

        // Check if "Proxy" appears as a path component
        if (dir.IndexOf("\\Proxy\\", StringComparison.OrdinalIgnoreCase) >= 0)
            return true;
        if (dir.IndexOf("/Proxy/", StringComparison.OrdinalIgnoreCase) >= 0)
            return true;

        return false;
    }

    /// <summary>
    /// Get the parent directory above the Proxy folder.
    /// </summary>
    private string GetParentOfProxy(string dir)
    {
        string parentDir = dir;
        while (true)
        {
            string dn = Path.GetFileName(parentDir) ?? "";
            if (string.Equals(dn, "Proxy", StringComparison.OrdinalIgnoreCase))
            {
                parentDir = Path.GetDirectoryName(parentDir);
                if (string.IsNullOrEmpty(parentDir)) return null;
            }
            else
            {
                break;
            }
        }
        return parentDir;
    }

    // ——————————————————————————————————————————————————————
    // RAW File Discovery
    // ——————————————————————————————————————————————————————

    /// <summary>
    /// Find the RAW file matching a proxy that lives inside a \Proxy\ directory.
    /// Looks in the parent directory (above Proxy) for .mp4/.MP4 files first.
    /// </summary>
    private string FindRawFromProxyDir(string proxyDir, string baseName)
    {
        string parentDir = GetParentOfProxy(proxyDir);
        if (string.IsNullOrEmpty(parentDir) || !Directory.Exists(parentDir))
            return null;

        return FindRawInDirectory(parentDir, baseName);
    }

    /// <summary>
    /// For .mov files NOT in a \Proxy\ folder, check if there's a .mp4 sibling
    /// in the same directory (indicating this .mov is a proxy alongside the raw).
    /// </summary>
    private string FindRawMp4Sibling(string dir, string baseName)
    {
        if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)) return null;

        // Only look for .mp4/.MP4 — NOT .mov (we already have the .mov)
        string[] rawExts = new string[] { ".mp4", ".MP4" };

        foreach (string ext in rawExts)
        {
            string cand = Path.Combine(dir, baseName + ext);
            if (File.Exists(cand)) return cand;
        }

        return null;
    }

    /// <summary>
    /// Search a directory for a RAW video file matching the given base name.
    /// Prioritizes .mp4/.MP4 to avoid re-matching .mov proxy files.
    /// Also handles _ABD suffix stripping for DJI drone clips.
    /// </summary>
    private string FindRawInDirectory(string dir, string baseName)
    {
        if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)) return null;

        // Priority order: .mp4 first (RAW), then .mov/.m4v/.mkv as fallbacks
        string[] rawExts = new string[] { ".mp4", ".MP4", ".mov", ".MOV", ".m4v", ".mkv" };

        // Try 1: Exact base name match
        foreach (string ext in rawExts)
        {
            string cand = Path.Combine(dir, baseName + ext);
            if (File.Exists(cand)) return cand;
        }

        // Try 2: Strip _ABD suffix (added during proxy transcode for DJI clips)
        if (baseName.EndsWith("_ABD", StringComparison.OrdinalIgnoreCase))
        {
            string strippedName = baseName.Substring(0, baseName.Length - 4);
            foreach (string ext in rawExts)
            {
                string cand = Path.Combine(dir, strippedName + ext);
                if (File.Exists(cand)) return cand;
            }
        }

        // Try 3: Wildcard search as last resort
        try
        {
            string searchPattern = baseName + ".*";
            string[] files = Directory.GetFiles(dir, searchPattern);
            foreach (string f in files)
            {
                string e = Path.GetExtension(f).ToLower();
                if (e == ".mp4" || e == ".m4v" || e == ".mkv") return f;
            }

            // If _ABD stripped, try wildcard with stripped name too
            if (baseName.EndsWith("_ABD", StringComparison.OrdinalIgnoreCase))
            {
                string strippedName = baseName.Substring(0, baseName.Length - 4);
                files = Directory.GetFiles(dir, strippedName + ".*");
                foreach (string f in files)
                {
                    string e = Path.GetExtension(f).ToLower();
                    if (e == ".mp4" || e == ".m4v" || e == ".mkv") return f;
                }
            }
        }
        catch { }

        return null;
    }

    // ——————————————————————————————————————————————————————
    // Media Pool Management
    // ——————————————————————————————————————————————————————

    /// <summary>
    /// Get existing media from pool or add new media. Deduplicates using cache.
    /// </summary>
    private Media GetOrAddMedia(Project proj, string path)
    {
        // Check cache first
        if (rawMediaCache.ContainsKey(path))
            return rawMediaCache[path];

        // Check if already in MediaPool
        foreach (Media m in proj.MediaPool)
        {
            try
            {
                if (m != null && !string.IsNullOrEmpty(m.FilePath) &&
                    m.FilePath.Equals(path, StringComparison.OrdinalIgnoreCase))
                {
                    rawMediaCache[path] = m;
                    return m;
                }
            }
            catch { }
        }

        // Add new media to pool
        try
        {
            Media newMedia = proj.MediaPool.AddMedia(path);
            if (newMedia != null)
            {
                rawMediaCache[path] = newMedia;
            }
            return newMedia;
        }
        catch (Exception ex)
        {
            diagLog.AppendLine("  ❌ AddMedia error: " + ex.Message);
            return null;
        }
    }

    // ——————————————————————————————————————————————————————
    // Pan/Crop Conforming
    // ——————————————————————————————————————————————————————

    /// <summary>
    /// Remaps Event Pan/Crop keyframes from 9:16 proxy space (2160x3840) to the
    /// 9:16 active video area (1215x2160) inside a 3840x2160 raw container.
    /// Preserves all custom zooms, pans, rotations, and animation keyframes.
    /// </summary>
    private void ConformPanCropForRaw(VideoEvent ve, VideoStream rawVs)
    {
        if (ve == null || ve.VideoMotion == null || ve.VideoMotion.Keyframes.Count == 0) return;
        if (rawVs == null || rawVs.Width != 3840 || rawVs.Height != 2160) return;

        // CRITICAL: Disable MaintainAspectRatio and enable ScaleToFill
        // This stops VEGAS from letterboxing the raw 16:9 container on the 9:16 project canvas,
        // allowing the 9:16 Pan/Crop frame to expand and fill the vertical canvas full bleed.
        ve.MaintainAspectRatio = false;
        ve.VideoMotion.ScaleToFill = true;

        const float scale = 0.5625f;       // 1215 / 2160 = 2160 / 3840 = 9 / 16
        const float offsetX = 1312.5f;     // (3840 - 1215) / 2
        const float activeVideoW = 1215.0f;
        const float activeVideoH = 2160.0f;

        foreach (VideoMotionKeyframe kf in ve.VideoMotion.Keyframes)
        {
            if (kf == null || kf.Bounds == null) continue;

            VideoMotionVertex tl = kf.Bounds.TopLeft;
            VideoMotionVertex tr = kf.Bounds.TopRight;
            VideoMotionVertex br = kf.Bounds.BottomRight;
            VideoMotionVertex bl = kf.Bounds.BottomLeft;
            if (tl == null || tr == null || br == null || bl == null) continue;

            double w = Math.Sqrt(Math.Pow(tr.X - tl.X, 2) + Math.Pow(tr.Y - tl.Y, 2));
            double h = Math.Sqrt(Math.Pow(tl.X - bl.X, 2) + Math.Pow(tl.Y - bl.Y, 2));

            // If already conformed to RAW active video:
            // Center X is in [1500, 2340], Height <= 2160.5, and Width <= 1215.5
            if (kf.Center != null && kf.Center.X >= 1500.0f && kf.Center.X <= 2340.0f && h <= 2160.5 && w <= 1215.5)
            {
                continue;
            }

            // Case 1: Vegas reset the keyframe to full 16:9 container (Width ~3840, Height ~2160)
            if (w > 3000.0 && Math.Abs(h - 2160.0) < 100.0)
            {
                double angleRad = kf.Rotation;
                float halfW = activeVideoW / 2.0f;
                float halfH = activeVideoH / 2.0f;
                float cx = 1920.0f;
                float cy = 1080.0f;

                float cosA = (float)Math.Cos(angleRad);
                float sinA = (float)Math.Sin(angleRad);

                VideoMotionVertex newTL = new VideoMotionVertex(cx + (-halfW * cosA - -halfH * sinA), cy + (-halfW * sinA + -halfH * cosA));
                VideoMotionVertex newTR = new VideoMotionVertex(cx + ( halfW * cosA - -halfH * sinA), cy + ( halfW * sinA + -halfH * cosA));
                VideoMotionVertex newBR = new VideoMotionVertex(cx + ( halfW * cosA -  halfH * sinA), cy + ( halfW * sinA +  halfH * cosA));
                VideoMotionVertex newBL = new VideoMotionVertex(cx + (-halfW * cosA -  halfH * sinA), cy + (-halfW * sinA +  halfH * cosA));

                kf.Bounds = new VideoMotionBounds(newTL, newTR, newBR, newBL);
            }
            // Case 2: Keyframe is in proxy coordinate space (2160 x 3840)
            // Transform all 4 corner vertices into 4K RAW active video area
            else
            {
                VideoMotionVertex newTL = new VideoMotionVertex(offsetX + tl.X * scale, tl.Y * scale);
                VideoMotionVertex newTR = new VideoMotionVertex(offsetX + tr.X * scale, tr.Y * scale);
                VideoMotionVertex newBR = new VideoMotionVertex(offsetX + br.X * scale, br.Y * scale);
                VideoMotionVertex newBL = new VideoMotionVertex(offsetX + bl.X * scale, bl.Y * scale);

                kf.Bounds = new VideoMotionBounds(newTL, newTR, newBR, newBL);
            }
        }
    }
}
