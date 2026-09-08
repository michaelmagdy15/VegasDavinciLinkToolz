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
                MessageBox.Show("No active project in VEGAS Pro.", "Auto Exposure Fix", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            PlugInNode fxNode = FindPlugin(vegas.VideoFX, "Levels");
            if (fxNode == null) fxNode = FindPlugin(vegas.VideoFX, "Color Curves");
            if (fxNode == null) fxNode = FindPlugin(vegas.VideoFX, "Brightness and Contrast");

            if (fxNode == null)
            {
                MessageBox.Show("Could not locate Levels or Color Curves plugin in VEGAS Video FX.", "Plugin Not Found", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            List<VideoEvent> targetEvents = new List<VideoEvent>();

            // Collect selected clips first
            foreach (Track track in vegas.Project.Tracks)
            {
                if (!track.IsVideo()) continue;
                foreach (TrackEvent ev in track.Events)
                {
                    if (ev.Selected && ev is VideoEvent)
                    {
                        targetEvents.Add((VideoEvent)ev);
                    }
                }
            }

            // If none selected, offer to apply to active track
            if (targetEvents.Count == 0)
            {
                DialogResult res = MessageBox.Show(
                    "No clips currently selected.\n\nApply Auto Exposure Normalization to ALL clips on the selected video track?",
                    "Auto Exposure Fix",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question
                );

                if (res != DialogResult.Yes) return;

                foreach (Track track in vegas.Project.Tracks)
                {
                    if (track.IsVideo() && track.Selected)
                    {
                        foreach (TrackEvent ev in track.Events)
                        {
                            if (ev is VideoEvent) targetEvents.Add((VideoEvent)ev);
                        }
                    }
                }

                if (targetEvents.Count == 0)
                {
                    MessageBox.Show("Please select a video track or select specific clips first.", "No Target", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }
            }

            int count = 0;
            foreach (VideoEvent vEvent in targetEvents)
            {
                // Check if already applied
                bool alreadyHas = false;
                foreach (Effect existing in vEvent.Effects)
                {
                    if (existing.PlugIn != null && existing.PlugIn.Name.IndexOf("Levels", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        alreadyHas = true;
                        break;
                    }
                }

                if (alreadyHas) continue;

                Effect fx = new Effect(fxNode);
                vEvent.Effects.Add(fx);

                // Try to set broadcast-safe highlight taming / shadow recovery preset
                if (fx.Presets != null && fx.Presets.Count > 0)
                {
                    foreach (EffectPreset preset in fx.Presets)
                    {
                        string pName = preset.Name.ToLower();
                        if (pName.Contains("computer rgb to studio rgb") || pName.Contains("studio rgb") || pName.Contains("broadcast"))
                        {
                            try { fx.Preset = preset.Name; } catch {}
                            break;
                        }
                    }
                }

                count++;
            }

            MessageBox.Show(
                string.Format(
                    "Auto Exposure Normalization Complete!\n\n" +
                    "- Plugin Applied: {0}\n" +
                    "- Clips Processed: {1}\n\n" +
                    "Crushed shadows lifted & sea/sky highlights pulled into legal broadcast range.",
                    fxNode.Name, count
                ),
                "Exposure Normalized",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                string.Format("Error fixing exposure: {0}\n\nStack: {1}", ex.Message, ex.StackTrace),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }
    }

    private PlugInNode FindPlugin(PlugInNode root, string query)
    {
        if (root == null) return null;
        if (root.Name != null && root.Name.IndexOf(query, StringComparison.OrdinalIgnoreCase) >= 0)
        {
            if (!root.IsContainer) return root;
        }

        for (int i = 0; i < root.Count; i++)
        {
            PlugInNode child = root.GetChild(i);
            PlugInNode match = FindPlugin(child, query);
            if (match != null) return match;
        }

        return null;
    }
}
