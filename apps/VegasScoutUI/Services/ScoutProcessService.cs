using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using VegasScoutUI.Models;

namespace VegasScoutUI.Services;

public class ScoutProgressEventArgs : EventArgs
{
    public int Current { get; set; }
    public int Total { get; set; }
    public string CurrentFile { get; set; } = string.Empty;
    public int CutsFound { get; set; }
    public double Percent { get; set; }
}

public class ScoutCompleteEventArgs : EventArgs
{
    public int TotalFiles { get; set; }
    public int TotalCuts { get; set; }
    public double TotalDurationMinutes { get; set; }
    public double ElapsedSeconds { get; set; }
    public string ManifestPath { get; set; } = string.Empty;
}

public class ScoutProcessService
{
    private Process? _activeProcess;
    private CancellationTokenSource? _cts;

    public event EventHandler<ScoutProgressEventArgs>? ProgressUpdated;
    public event EventHandler<SelectClipItem>? CutFound;
    public event EventHandler<ScoutCompleteEventArgs>? Completed;
    public event EventHandler<string>? ErrorOccurred;

    public bool IsRunning => _activeProcess != null && !_activeProcess.HasExited;

    public async Task StartScoutAsync(
        string folderPath,
        double targetDuration = 3.5,
        int maxPeaks = 3,
        string trackMode = "location",
        int maxWorkers = 3)
    {
        if (IsRunning)
        {
            throw new InvalidOperationException("Scout is already running.");
        }

        _cts = new CancellationTokenSource();

        await Task.Run(() =>
        {
            try
            {
                // Resolve repo root where core/scout_cli.py lives
                string currentDir = AppDomain.CurrentDomain.BaseDirectory;
                string scriptPath = Path.GetFullPath(Path.Combine(currentDir, "..", "..", "..", "..", "..", "core", "scout_cli.py"));

                if (!File.Exists(scriptPath))
                {
                    // Fallback to relative to executable directory or root
                    string altPath = Path.GetFullPath(Path.Combine(currentDir, "core", "scout_cli.py"));
                    if (File.Exists(altPath))
                    {
                        scriptPath = altPath;
                    }
                }

                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = string.Format(
                        System.Globalization.CultureInfo.InvariantCulture,
                        "\"{0}\" --folder \"{1}\" --target-duration {2:0.1} --max-peaks {3} --track-mode {4} --max-workers {5}",
                        scriptPath,
                        folderPath,
                        targetDuration,
                        maxPeaks,
                        trackMode,
                        maxWorkers
                    ),
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = System.Text.Encoding.UTF8,
                    StandardErrorEncoding = System.Text.Encoding.UTF8,
                };

                _activeProcess = new Process { StartInfo = psi };
                _activeProcess.OutputDataReceived += (s, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        ParseOutputLine(e.Data);
                    }
                };

                _activeProcess.ErrorDataReceived += (s, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        Debug.WriteLine("[Python Error] " + e.Data);
                    }
                };

                _activeProcess.Start();
                _activeProcess.BeginOutputReadLine();
                _activeProcess.BeginErrorReadLine();

                _activeProcess.WaitForExit();
            }
            catch (Exception ex)
            {
                ErrorOccurred?.Invoke(this, ex.Message);
            }
            finally
            {
                _activeProcess = null;
            }
        }, _cts.Token);
    }

    public void Cancel()
    {
        try
        {
            if (_activeProcess != null && !_activeProcess.HasExited)
            {
                _activeProcess.Kill(true);
            }
            _cts?.Cancel();
        }
        catch {}
    }

    private void ParseOutputLine(string line)
    {
        try
        {
            using JsonDocument doc = JsonDocument.Parse(line);
            JsonElement root = doc.RootElement;

            if (!root.TryGetProperty("event", out JsonElement evElem)) return;
            string? ev = evElem.GetString();

            if (ev == "progress")
            {
                int current = root.GetProperty("current").GetInt32();
                int total = root.GetProperty("total").GetInt32();
                string currentFile = root.GetProperty("current_file").GetString() ?? "";
                int cutsFound = root.GetProperty("cuts_found").GetInt32();
                double percent = root.GetProperty("percent").GetDouble();

                ProgressUpdated?.Invoke(this, new ScoutProgressEventArgs
                {
                    Current = current,
                    Total = total,
                    CurrentFile = currentFile,
                    CutsFound = cutsFound,
                    Percent = percent
                });
            }
            else if (ev == "cut_found")
            {
                if (root.TryGetProperty("cut", out JsonElement cutElem))
                {
                    SelectClipItem item = new SelectClipItem
                    {
                        Name = cutElem.GetProperty("name").GetString() ?? "",
                        MediaPath = cutElem.GetProperty("media_path").GetString() ?? "",
                        SourceInMs = cutElem.GetProperty("source_in_ms").GetDouble(),
                        LengthMs = cutElem.GetProperty("length_ms").GetDouble(),
                        Score = cutElem.GetProperty("score").GetDouble(),
                        Label = cutElem.GetProperty("label").GetString() ?? "",
                        TrackName = cutElem.GetProperty("track_name").GetString() ?? ""
                    };
                    CutFound?.Invoke(this, item);
                }
            }
            else if (ev == "complete")
            {
                int totalFiles = root.TryGetProperty("total_files", out JsonElement tf) ? tf.GetInt32() : 0;
                int totalCuts = root.TryGetProperty("total_cuts", out JsonElement tc) ? tc.GetInt32() : 0;
                double totalDur = root.TryGetProperty("total_duration_minutes", out JsonElement td) ? td.GetDouble() : 0.0;
                double elapsed = root.TryGetProperty("elapsed_seconds", out JsonElement es) ? es.GetDouble() : 0.0;
                string manifest = root.TryGetProperty("manifest_path", out JsonElement mp) ? (mp.GetString() ?? "") : "";

                Completed?.Invoke(this, new ScoutCompleteEventArgs
                {
                    TotalFiles = totalFiles,
                    TotalCuts = totalCuts,
                    TotalDurationMinutes = totalDur,
                    ElapsedSeconds = elapsed,
                    ManifestPath = manifest
                });
            }
            else if (ev == "error")
            {
                string msg = root.GetProperty("message").GetString() ?? "Unknown error";
                ErrorOccurred?.Invoke(this, msg);
            }
        }
        catch
        {
            // Ignore non-json debug lines
        }
    }
}
