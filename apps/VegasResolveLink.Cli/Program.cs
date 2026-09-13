using System;
using System.IO;
using System.Diagnostics;
using VegasResolveLink.Engine;

namespace VegasResolveLink.Cli
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("====================================================================");
            Console.WriteLine("  VEGAS Pro <--> DaVinci Resolve Studio Universal Live Link CLI");
            Console.WriteLine("====================================================================");
            Console.WriteLine();

            string bridgeDir = VegasEnvironment.GetBridgeDirectory();
            Console.WriteLine($"[Bridge Directory] {bridgeDir}");
            Console.WriteLine();

            // 1. Detect VEGAS Pro
            Console.WriteLine("[1] Detecting VEGAS Pro Installations:");
            var vegasInstalls = VegasEnvironment.DetectVegasInstallations();
            if (vegasInstalls.Count == 0)
            {
                Console.WriteLine("    [!] No VEGAS Pro installations found in standard paths.");
            }
            else
            {
                foreach (var v in vegasInstalls)
                {
                    Console.WriteLine($"    [+] {v.Name} ({v.Version})");
                    Console.WriteLine($"        Install: {v.InstallDir}");
                    Console.WriteLine($"        Scripts: {v.ScriptMenuDir}");
                }
            }
            Console.WriteLine();

            // 2. Detect DaVinci Resolve
            Console.WriteLine("[2] Detecting DaVinci Resolve Studio:");
            var resolve = VegasEnvironment.DetectResolveInstallation();
            if (resolve.IsAvailable)
            {
                Console.WriteLine($"    [+] DaVinci Resolve detected!");
                Console.WriteLine($"        App Directory: {resolve.AppDir}");
                Console.WriteLine($"        FusionScript:  {resolve.FusionScriptDll}");
            }
            else
            {
                Console.WriteLine("    [!] DaVinci Resolve fusionscript.dll not found.");
            }
            Console.WriteLine();

            // 3. Check Active Manifests
            Console.WriteLine("[3] Checking Live Timeline Status:");
            string manifestPath = VegasEnvironment.GetTimelineManifestPath();
            if (File.Exists(manifestPath))
            {
                var manifest = TimelineManifest.LoadFromFile(manifestPath);
                if (manifest != null)
                {
                    Console.WriteLine($"    [OK] Active Manifest: '{manifest.ProjectName}' ({manifest.FrameRate:F2} fps, {manifest.Width}x{manifest.Height})");
                    Console.WriteLine($"         Total Tracks: {manifest.Tracks.Count}");
                    int totalClips = 0;
                    foreach (var t in manifest.Tracks) totalClips += t.Clips.Count;
                    Console.WriteLine($"         Total Clips:  {totalClips}");
                }
            }
            else
            {
                Console.WriteLine($"    [!] No timeline manifest yet at: {manifestPath}");
                Console.WriteLine("        In VEGAS Pro, click 'Tools -> Scripting -> Send to DaVinci Resolve'.");
            }
            Console.WriteLine();

            // 4. Check Deep Scan Status
            string deepScanPath = VegasEnvironment.GetDeepScanPath();
            if (File.Exists(deepScanPath))
            {
                Console.WriteLine($"[4] Deep Project Scan Manifest detected: {deepScanPath}");
                string summaryMd = Path.Combine(bridgeDir, "vegas_deep_scan_summary.md");
                if (File.Exists(summaryMd))
                {
                    Console.WriteLine($"    Summary report: {summaryMd}");
                }
            }
            else
            {
                Console.WriteLine("[4] Deep Project Scan Manifest:");
                Console.WriteLine("    To scan in-memory OFX parameters, open your project in VEGAS Pro and run:");
                Console.WriteLine("    'Tools -> Scripting -> Deep Scan Project'");
            }

            Console.WriteLine();
            Console.WriteLine("====================================================================");
        }
    }
}
