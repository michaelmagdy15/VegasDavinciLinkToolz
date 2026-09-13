using System;
using System.IO;
using System.Collections.Generic;

namespace VegasResolveLink.Engine
{
    public class VegasInstallation
    {
        public string Name { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string InstallDir { get; set; } = string.Empty;
        public string? Executable { get; set; }
        public string ScriptMenuDir { get; set; } = string.Empty;
        public bool IsRunning { get; set; }
    }

    public class ResolveInstallation
    {
        public string? AppDir { get; set; }
        public string? FusionScriptDll { get; set; }
        public string? ScriptModulesDir { get; set; }
        public bool IsAvailable { get; set; }
        public bool IsRunning { get; set; }
    }

    public static class VegasEnvironment
    {
        public static string GetBridgeDirectory()
        {
            string userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            string dir = Path.Combine(userProfile, ".timeline_bridge");
            if (!Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }
            return dir;
        }

        public static string GetTimelineManifestPath()
        {
            return Path.Combine(GetBridgeDirectory(), "vegas_timeline.json");
        }

        public static string GetDeepScanPath()
        {
            return Path.Combine(GetBridgeDirectory(), "vegas_deep_scan.json");
        }

        public static List<VegasInstallation> DetectVegasInstallations()
        {
            var results = new List<VegasInstallation>();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            string progFiles = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
            string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);

            var candidates = new (string RelPath, string Name, string Version)[]
            {
                (@"BorisFX\Vegas Pro 2026", "BorisFX Vegas Pro 2026", "2026.0"),
                (@"VEGAS\VEGAS Pro 23.0", "VEGAS Pro 23.0", "23.0"),
                (@"VEGAS\Vegas Pro 22", "VEGAS Pro 22.0", "22.0"),
                (@"VEGAS\VEGAS Pro 21.0", "VEGAS Pro 21.0", "21.0"),
                (@"VEGAS\VEGAS Pro 20.0", "VEGAS Pro 20.0", "20.0"),
                (@"Sony\Vegas Pro 13.0", "Sony Vegas Pro 13.0", "13.0"),
            };

            foreach (var (rel, name, ver) in candidates)
            {
                string fullPath = Path.Combine(progFiles, rel);
                if (Directory.Exists(fullPath) && !seen.Contains(fullPath))
                {
                    seen.Add(fullPath);
                    string? exe = null;
                    try
                    {
                        foreach (string f in Directory.GetFiles(fullPath, "*.exe"))
                        {
                            if (Path.GetFileName(f).IndexOf("vegas", StringComparison.OrdinalIgnoreCase) >= 0)
                            {
                                exe = f;
                                break;
                            }
                        }
                    }
                    catch {}

                    string scriptDir = Path.Combine(appData, "VEGAS Pro", ver, "Script Menu");
                    if (!Directory.Exists(Path.GetDirectoryName(scriptDir)))
                    {
                        scriptDir = Path.Combine(fullPath, "Script Menu");
                    }

                    results.Add(new VegasInstallation
                    {
                        Name = name,
                        Version = ver,
                        InstallDir = fullPath,
                        Executable = exe,
                        ScriptMenuDir = scriptDir
                    });
                }
            }

            return results;
        }

        public static ResolveInstallation DetectResolveInstallation()
        {
            string progFiles = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
            string progData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);

            string resolveDir = Path.Combine(progFiles, @"Blackmagic Design\DaVinci Resolve");
            string fusionDll = Path.Combine(resolveDir, "fusionscript.dll");
            string modulesDir = Path.Combine(progData, @"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules");

            bool available = File.Exists(fusionDll);

            return new ResolveInstallation
            {
                AppDir = Directory.Exists(resolveDir) ? resolveDir : null,
                FusionScriptDll = available ? fusionDll : null,
                ScriptModulesDir = Directory.Exists(modulesDir) ? modulesDir : null,
                IsAvailable = available
            };
        }
    }
}
