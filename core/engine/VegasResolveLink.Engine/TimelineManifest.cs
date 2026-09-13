using System;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Collections.Generic;

namespace VegasResolveLink.Engine
{
    public class TimelineManifest
    {
        [JsonPropertyName("project_name")]
        public string ProjectName { get; set; } = "Untitled";

        [JsonPropertyName("project_file")]
        public string? ProjectFile { get; set; }

        [JsonPropertyName("frame_rate")]
        public double FrameRate { get; set; } = 29.97;

        [JsonPropertyName("width")]
        public int Width { get; set; } = 1920;

        [JsonPropertyName("height")]
        public int Height { get; set; } = 1080;

        [JsonPropertyName("markers")]
        public List<MarkerModel> Markers { get; set; } = new();

        [JsonPropertyName("regions")]
        public List<RegionModel> Regions { get; set; } = new();

        [JsonPropertyName("tracks")]
        public List<TrackModel> Tracks { get; set; } = new();

        public static TimelineManifest? LoadFromFile(string path)
        {
            if (!File.Exists(path)) return null;
            string json = File.ReadAllText(path);
            return JsonSerializer.Deserialize<TimelineManifest>(json, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });
        }

        public void SaveToFile(string path)
        {
            string json = JsonSerializer.Serialize(this, new JsonSerializerOptions
            {
                WriteIndented = true
            });
            File.WriteAllText(path, json);
        }
    }

    public class MarkerModel
    {
        [JsonPropertyName("label")]
        public string Label { get; set; } = string.Empty;

        [JsonPropertyName("position_ms")]
        public double PositionMs { get; set; }
    }

    public class RegionModel
    {
        [JsonPropertyName("label")]
        public string Label { get; set; } = string.Empty;

        [JsonPropertyName("position_ms")]
        public double PositionMs { get; set; }

        [JsonPropertyName("length_ms")]
        public double LengthMs { get; set; }
    }

    public class TrackModel
    {
        [JsonPropertyName("index")]
        public int Index { get; set; }

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("is_video")]
        public bool IsVideo { get; set; } = true;

        [JsonPropertyName("is_audio")]
        public bool IsAudio { get; set; }

        [JsonPropertyName("composite_mode")]
        public string CompositeMode { get; set; } = "SourceAlpha";

        [JsonPropertyName("composite_level")]
        public double CompositeLevel { get; set; } = 1.0;

        [JsonPropertyName("mute")]
        public bool Mute { get; set; }

        [JsonPropertyName("solo")]
        public bool Solo { get; set; }

        [JsonPropertyName("volume_db")]
        public double VolumeDb { get; set; }

        [JsonPropertyName("pan")]
        public double Pan { get; set; }

        [JsonPropertyName("effects")]
        public List<EffectModel> Effects { get; set; } = new();

        [JsonPropertyName("clips")]
        public List<ClipModel> Clips { get; set; } = new();

        [JsonPropertyName("events")]
        public List<ClipModel> Events { get; set; } = new();
    }

    public class ClipModel
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("media_path")]
        public string MediaPath { get; set; } = string.Empty;

        [JsonPropertyName("timeline_start_ms")]
        public double TimelineStartMs { get; set; }

        [JsonPropertyName("timeline_length_ms")]
        public double TimelineLengthMs { get; set; }

        [JsonPropertyName("source_in_ms")]
        public double SourceInMs { get; set; }

        [JsonPropertyName("playback_rate")]
        public double PlaybackRate { get; set; } = 1.0;

        [JsonPropertyName("is_reversed")]
        public bool IsReversed { get; set; }

        [JsonPropertyName("rotation_angle")]
        public double RotationAngle { get; set; }

        [JsonPropertyName("zoom_x")]
        public double ZoomX { get; set; } = 1.0;

        [JsonPropertyName("zoom_y")]
        public double ZoomY { get; set; } = 1.0;

        [JsonPropertyName("pan_x")]
        public double PanX { get; set; }

        [JsonPropertyName("pan_y")]
        public double PanY { get; set; }

        [JsonPropertyName("crop_left")]
        public double CropLeft { get; set; }

        [JsonPropertyName("crop_right")]
        public double CropRight { get; set; }

        [JsonPropertyName("crop_top")]
        public double CropTop { get; set; }

        [JsonPropertyName("crop_bottom")]
        public double CropBottom { get; set; }

        [JsonPropertyName("group_id")]
        public object? GroupId { get; set; }

        [JsonPropertyName("volume")]
        public double Volume { get; set; }

        [JsonPropertyName("mute")]
        public bool Mute { get; set; }

        [JsonPropertyName("effects")]
        public List<EffectModel> Effects { get; set; } = new();
    }

    public class EffectModel
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("unique_id")]
        public string UniqueId { get; set; } = string.Empty;

        [JsonPropertyName("class_id")]
        public string ClassId { get; set; } = string.Empty;

        [JsonPropertyName("is_ofx")]
        public bool IsOfx { get; set; }

        [JsonPropertyName("bypass")]
        public bool Bypass { get; set; }

        [JsonPropertyName("preset")]
        public string Preset { get; set; } = string.Empty;

        [JsonPropertyName("ofx_label")]
        public string? OfxLabel { get; set; }

        [JsonPropertyName("ofx_plugin_path")]
        public string? OfxPluginPath { get; set; }

        [JsonPropertyName("parameters")]
        public List<ParameterModel> Parameters { get; set; } = new();
    }

    public class ParameterModel
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("label")]
        public string Label { get; set; } = string.Empty;

        [JsonPropertyName("type")]
        public string Type { get; set; } = string.Empty;

        [JsonPropertyName("enabled")]
        public bool Enabled { get; set; } = true;

        [JsonPropertyName("value")]
        public object? Value { get; set; }
    }
}
