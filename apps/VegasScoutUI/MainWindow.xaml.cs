using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Pickers;
using VegasScoutUI.Models;
using VegasScoutUI.Services;
using WinRT.Interop;

namespace VegasScoutUI;

public sealed partial class MainWindow : Window
{
    private readonly ScoutProcessService _scoutService = new();
    private readonly ObservableCollection<SelectClipItem> _allClips = new();
    private readonly ObservableCollection<SelectClipItem> _filteredClips = new();
    private string _currentManifestPath = string.Empty;

    public MainWindow()
    {
        InitializeComponent();
        ListSelects.ItemsSource = _filteredClips;

        // Subscribe to process service events
        _scoutService.ProgressUpdated += OnProgressUpdated;
        _scoutService.CutFound += OnCutFound;
        _scoutService.Completed += OnCompleted;
        _scoutService.ErrorOccurred += OnErrorOccurred;

        // Default folder test
        string defaultFolder = @"F:\Arrow\arrow kite surf 2\sorted 2\drone";
        if (Directory.Exists(defaultFolder))
        {
            TxtFolderPath.Text = defaultFolder;
        }
        else
        {
            // Try looking for drone folder with special char
            string parent = @"F:\Arrow\arrow kite surf 2\sorted 2";
            if (Directory.Exists(parent))
            {
                var d = Directory.GetDirectories(parent).FirstOrDefault(x => x.ToLower().Contains("drone"));
                if (!string.IsNullOrEmpty(d))
                {
                    TxtFolderPath.Text = d;
                }
            }
        }
    }

    #region Drag and Drop & Folder Browse

    private void DropZone_DragOver(object sender, DragEventArgs e)
    {
        e.AcceptedOperation = DataPackageOperation.Copy;
        e.DragUIOverride.Caption = "Drop footage folder to scan";
        e.DragUIOverride.IsCaptionVisible = true;
    }

    private async void DropZone_Drop(object sender, DragEventArgs e)
    {
        if (e.DataView.Contains(StandardDataFormats.StorageItems))
        {
            var items = await e.DataView.GetStorageItemsAsync();
            if (items.Count > 0 && items[0] is StorageFolder folder)
            {
                TxtFolderPath.Text = folder.Path;
            }
            else if (items.Count > 0 && items[0] is StorageFile file)
            {
                string? dir = Path.GetDirectoryName(file.Path);
                if (!string.IsNullOrEmpty(dir))
                {
                    TxtFolderPath.Text = dir;
                }
            }
        }
    }

    private async void BtnBrowse_Click(object sender, RoutedEventArgs e)
    {
        var folderPicker = new FolderPicker();
        folderPicker.SuggestedStartLocation = PickerLocationId.ComputerFolder;
        folderPicker.FileTypeFilter.Add("*");

        IntPtr hwnd = WindowNative.GetWindowHandle(this);
        InitializeWithWindow.Initialize(folderPicker, hwnd);

        StorageFolder folder = await folderPicker.PickSingleFolderAsync();
        if (folder != null)
        {
            TxtFolderPath.Text = folder.Path;
        }
    }

    private void TxtFolderPath_TextChanged(object sender, TextChangedEventArgs e)
    {
        string path = TxtFolderPath.Text.Trim();
        if (Directory.Exists(path))
        {
            try
            {
                var videoExts = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { ".mp4", ".mov", ".m4v", ".avi" };
                int fileCount = 0;
                foreach (var f in Directory.EnumerateFiles(path, "*.*", SearchOption.AllDirectories))
                {
                    if (videoExts.Contains(Path.GetExtension(f)) && !Path.GetFileName(f).StartsWith("._"))
                    {
                        fileCount++;
                    }
                }

                int subCount = Directory.GetDirectories(path).Length;

                TxtFileCount.Text = string.Format("{0} video files found", fileCount);
                TxtSubfolders.Text = string.Format("{0} location folders", subCount);
                PnlFolderStats.Visibility = Visibility.Visible;
                BtnStartScout.IsEnabled = fileCount > 0;
            }
            catch
            {
                PnlFolderStats.Visibility = Visibility.Collapsed;
            }
        }
        else
        {
            PnlFolderStats.Visibility = Visibility.Collapsed;
        }
    }

    #endregion

    #region Sliders & Configuration

    private void SliderDuration_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
    {
        if (TxtCutDurationValue != null)
        {
            TxtCutDurationValue.Text = string.Format("{0:0.1}s", e.NewValue);
        }
    }

    private void SliderMaxPeaks_ValueChanged(object sender, Microsoft.UI.Xaml.Controls.Primitives.RangeBaseValueChangedEventArgs e)
    {
        if (TxtMaxPeaksValue != null)
        {
            TxtMaxPeaksValue.Text = string.Format("{0} cuts", (int)e.NewValue);
        }
    }

    #endregion

    #region AI Culling Execution

    private async void BtnStartScout_Click(object sender, RoutedEventArgs e)
    {
        string folder = TxtFolderPath.Text.Trim();
        if (!Directory.Exists(folder))
        {
            ShowNotification("Please select a valid footage folder.", InfoBarSeverity.Warning);
            return;
        }

        // Reset UI
        _allClips.Clear();
        _filteredClips.Clear();
        TxtBadgeCount.Text = "0 Cuts";
        ProgressBarScout.Value = 0;
        ProgressBarScout.Visibility = Visibility.Visible;
        PnlStatusDetails.Visibility = Visibility.Visible;
        TxtProgressPercent.Visibility = Visibility.Visible;
        BtnStartScout.Visibility = Visibility.Collapsed;
        BtnCancel.Visibility = Visibility.Visible;
        BtnSendToVegas.IsEnabled = false;
        BtnOpenManifest.IsEnabled = false;

        double targetDuration = SliderDuration.Value;
        int maxPeaks = (int)SliderMaxPeaks.Value;
        string trackMode = (ComboTrackMode.SelectedItem as ComboBoxItem)?.Tag?.ToString() ?? "location";

        ShowNotification("Running hardware-accelerated motion scout on GPU...", InfoBarSeverity.Informational);

        try
        {
            await _scoutService.StartScoutAsync(
                folderPath: folder,
                targetDuration: targetDuration,
                maxPeaks: maxPeaks,
                trackMode: trackMode,
                maxWorkers: 3
            );
        }
        catch (Exception ex)
        {
            ShowNotification("Execution error: " + ex.Message, InfoBarSeverity.Error);
            ResetExecutionUI();
        }
    }

    private void BtnCancel_Click(object sender, RoutedEventArgs e)
    {
        _scoutService.Cancel();
        ShowNotification("AI Culling was cancelled.", InfoBarSeverity.Warning);
        ResetExecutionUI();
    }

    private void ResetExecutionUI()
    {
        DispatcherQueue.TryEnqueue(() =>
        {
            BtnStartScout.Visibility = Visibility.Visible;
            BtnCancel.Visibility = Visibility.Collapsed;
            ProgressBarScout.Visibility = Visibility.Collapsed;
            PnlStatusDetails.Visibility = Visibility.Collapsed;
            TxtProgressPercent.Visibility = Visibility.Collapsed;
        });
    }

    #endregion

    #region Background Event Handlers

    private void OnProgressUpdated(object? sender, ScoutProgressEventArgs e)
    {
        DispatcherQueue.TryEnqueue(() =>
        {
            ProgressBarScout.Value = e.Percent;
            TxtProgressPercent.Text = string.Format("{0:0}%", e.Percent);
            TxtStatusMessage.Text = string.Format("Scouting clip {0} of {1}: {2}", e.Current, e.Total, e.CurrentFile);
            TxtCutsCounter.Text = string.Format("{0} cuts detected", e.CutsFound);
        });
    }

    private void OnCutFound(object? sender, SelectClipItem item)
    {
        DispatcherQueue.TryEnqueue(() =>
        {
            _allClips.Add(item);
            ApplyFilter();
            TxtBadgeCount.Text = string.Format("{0} Cuts", _allClips.Count);
        });
    }

    private void OnCompleted(object? sender, ScoutCompleteEventArgs e)
    {
        DispatcherQueue.TryEnqueue(() =>
        {
            _currentManifestPath = e.ManifestPath;
            ResetExecutionUI();

            BtnSendToVegas.IsEnabled = true;
            BtnOpenManifest.IsEnabled = true;

            TxtSummaryFooter.Text = string.Format(
                "Completed in {0:0.1}s! {1} total cuts ({2:0.1} min) saved to manifest.",
                e.ElapsedSeconds,
                e.TotalCuts,
                e.TotalDurationMinutes
            );
            TxtManifestPath.Text = e.ManifestPath;

            ShowNotification(
                string.Format("Success! Found {0} action highlights across {1} clips ({2:0.1} min). Ready to import in VEGAS Pro 2026!", e.TotalCuts, e.TotalFiles, e.TotalDurationMinutes),
                InfoBarSeverity.Success
            );
        });
    }

    private void OnErrorOccurred(object? sender, string message)
    {
        DispatcherQueue.TryEnqueue(() =>
        {
            ShowNotification(message, InfoBarSeverity.Error);
            ResetExecutionUI();
        });
    }

    #endregion

    #region Filtering & Search

    private void TxtSearchCuts_TextChanged(object sender, TextChangedEventArgs e)
    {
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        string query = TxtSearchCuts?.Text?.Trim().ToLower() ?? "";
        _filteredClips.Clear();

        foreach (var c in _allClips)
        {
            if (string.IsNullOrEmpty(query) ||
                c.Name.ToLower().Contains(query) ||
                c.TrackName.ToLower().Contains(query) ||
                c.Label.ToLower().Contains(query))
            {
                _filteredClips.Add(c);
            }
        }
    }

    #endregion

    #region Export & VEGAS Pro Actions

    private async void BtnSendToVegas_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new ContentDialog
        {
            Title = "Import into VEGAS Pro 2026",
            Content = new StackPanel
            {
                Spacing = 12,
                Children =
                {
                    new TextBlock
                    {
                        Text = "The AI Selects Manifest is ready for VEGAS Pro!",
                        FontWeight = Microsoft.UI.Text.FontWeights.SemiBold
                    },
                    new TextBlock
                    {
                        Text = "To populate these cuts onto your timeline:\n\n" +
                               "1. Switch to VEGAS Pro 2026.\n" +
                               "2. Open your project or timeline.\n" +
                               "3. In the top menu, click: Tools ➔ Scripting ➔ Import AI Selects.\n" +
                               "4. Choose YES to place all cuts onto the organized location tracks.\n\n" +
                               "(Your rough cut tracks are 100% safe and will never be touched).",
                        TextWrapping = TextWrapping.Wrap
                    }
                }
            },
            CloseButtonText = "Got it",
            XamlRoot = this.Content.XamlRoot
        };

        await dialog.ShowAsync();
    }

    private void BtnOpenManifest_Click(object sender, RoutedEventArgs e)
    {
        if (!string.IsNullOrEmpty(_currentManifestPath) && File.Exists(_currentManifestPath))
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = "explorer.exe",
                Arguments = $"/select,\"{_currentManifestPath}\"",
                UseShellExecute = true
            });
        }
        else
        {
            string bridgeDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".timeline_bridge");
            if (Directory.Exists(bridgeDir))
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = "explorer.exe",
                    Arguments = $"\"{bridgeDir}\"",
                    UseShellExecute = true
                });
            }
        }
    }

    private void ShowNotification(string message, InfoBarSeverity severity)
    {
        InfoBarNotification.Message = message;
        InfoBarNotification.Severity = severity;
        InfoBarNotification.IsOpen = true;
    }

    #endregion
}
