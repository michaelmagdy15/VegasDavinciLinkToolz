# 🎬 VEGAS Pro 2026 & DaVinci Resolve Timeline Bridge — Master Documentation

> **Complete Technical Architecture, AI Action Scout System, Plugin Reference, and Operational Guide**  
> *Cut in VEGAS Pro 2026. Grade in DaVinci Resolve Studio. Zero broken timelines, zero lost frames.*

---

## 📑 Table of Contents
1. [Executive Overview](#1-executive-overview)
2. [AI Action Scout Engine](#2-ai-action-scout-engine)
   - [Hardware-Accelerated Frame Sampling](#hardware-accelerated-frame-sampling)
   - [10-Bit HEVC & Color Profile Handling](#10-bit-hevc--color-profile-handling)
   - [Multi-Peak Action & Promo Extraction Algorithm](#multi-peak-action--promo-extraction-algorithm)
   - [Case Study: Arrow Kitesurf 2026 (4K Drone Footage)](#case-study-arrow-kitesurf-2026-4k-drone-footage)
3. [VEGAS Pro 2026 Automation & Scripting Suite](#3-vegas-pro-2026-automation--scripting-suite)
   - [Import AI Selects (`ImportAISelects.cs`)](#import-ai-selects-importaiselectscs)
   - [The Complete 14-Plugin Suite](#the-complete-14-plugin-suite)
4. [Live Link & Bidirectional Synchronization](#4-live-link--bidirectional-synchronization)
5. [FastMCP Server (AI Assistant Integration)](#5-fastmcp-server-ai-assistant-integration)
6. [XML Cleaner & Standalone Desktop GUI](#6-xml-cleaner--standalone-desktop-gui)
7. [Step-by-Step Operator Manual](#7-step-by-step-operator-manual)

---

## 1. Executive Overview

**VegasDavinciLinkTool** is an end-to-end editorial ecosystem connecting **VEGAS Pro (including VEGAS Pro 2026, 23.0, and 22.0)** and **Blackmagic Design DaVinci Resolve Studio (21, 20, 19)**.

### Core Problems Solved
* **No Broken XML Roundtrips**: Eliminates "Media Offline", unreadable `file://localhost/` URI schemes, and parser crashes caused by proprietary MAGIX/Sony Track Motion or OFX effect blocks.
* **Direct Live Link**: 1-click bridge via internal scripting APIs without requiring intermediate XML file exports.
* **AI Action Scout**: High-throughput visual motion intelligence that turns hours of unorganized raw/drone footage into pre-trimmed highlight reels ready on the timeline in minutes.
* **VEGAS Pro Power Suite**: 14 native C# plugins directly accessible from `Tools -> Scripting` for instant timeline cleanup, speed ramps, audio fades, flash transitions, proxy toggling, and exposure fixes.
* **FastMCP Server**: Standardized Model Context Protocol server giving AI coding and editing assistants (Antigravity, Claude, Cursor) full inspection and control over NLE projects.

---

## 2. AI Action Scout Engine

The **AI Action Scout** (`core/ai_scout.py`) is an autonomous computer-vision analysis pipeline designed to solve the biggest bottleneck in extreme sports, documentary, and promo editing: **scrubbing through massive amounts of continuous footage to find usable cuts**.

```
[Raw 4K HEVC Video] ──► [RTX 4080 NVDEC GPU] ──► [160x90 Gray Frame Stream]
                                                          │
                                                          ▼
[VEGAS Pro 2026 Timeline] ◄── [Manifest JSON] ◄── [Motion Delta & Peak Detection]
```

### Hardware-Accelerated Frame Sampling
* **NVIDIA CUDA + NVDEC Acceleration**: Offloads video decoding directly to the GPU (tested on NVIDIA GeForce RTX 4080).
* **On-GPU Scaling (`scale_cuda`)**: Eliminates the severe PCIe bus bottleneck of moving uncompressed 4K frames to CPU memory. Frames are downsampled directly in VRAM to `160x90` before downloading.
* **Sample Rate**: Defaults to `1.0 fps` (1 frame per second), delivering maximum scanning throughput while retaining full temporal precision for finding peak action.

### 10-Bit HEVC & Color Profile Handling
Modern drone footage (such as DJI Mavic 3 / Air 3 D-Log M) uses **10-bit HEVC (`yuv420p10le`)**. 
* Standard 8-bit pipelines fail or produce garbled pixels when decoding 10-bit streams.
* The scout automatically detects bit-depth via `ffprobe` stream inspection:
  * **10-Bit Streams**: Uses `hwdownload,format=p010le`. The 16-bit Y-plane is unpacked via NumPy bit-shifting (`y_plane >> 8`) into 8-bit grayscale for motion delta computation.
  * **8-Bit Streams**: Uses `hwdownload,format=nv12` with direct uint8 Y-plane extraction.
  * **CPU Fallback**: Graceful fallback to `-vf fps=1,scale=160:90,format=gray` if hardware decoding is unavailable.

### Multi-Peak Action & Promo Extraction Algorithm
Standard motion scouts often grab only the single biggest movement in a file, which discards 95% of usable footage from long takes. The promo engine uses **dynamic multi-peak extraction**:

1. **Temporal Motion Energy**: Computes the mean absolute difference between adjacent sampled frames:
   $$\Delta_t = \frac{1}{W \times H} \sum_{x,y} |I_{t+1}(x,y) - I_t(x,y)|$$
2. **Convolution Smoothing**: Applies a uniform moving-average filter across the target duration ($\approx 3.5\text{s}$ sweet spot for promo edits).
3. **Primary Peak ($P_1$)**: Locates the global maximum (e.g. kiteloop takeoff, sharp carve, water spray).
4. **Secondary Peak ($P_2$)**: If clip duration $> 18\text{s}$, masks out a $\pm 8\text{s}$ exclusion radius around $P_1$ and selects the second highest peak (e.g. flat-water speed run).
5. **Tertiary Peak ($P_3$)**: If clip duration $> 55\text{s}$, masks out an additional $\pm 12\text{s}$ radius to select a third distinct moment (e.g. scenic lagoon flyover or rider reveal).
6. **Chronological Sorting**: Extracted cuts are ordered by timestamp so they sequence naturally on the timeline.

### Case Study: Arrow Kitesurf 2026 (4K Drone Footage)
Executed across 3 drone flight folders in `F:\Arrow\arrow kite surf 2\sorted 2\drone`:

| Location Track | Raw Clips Scanned | AI Selects Generated | Highlights & Visual Characteristics |
| :--- | :---: | :---: | :--- |
| **`[AI SELECTS] Drone - Dahab Blue Lagoon`** | 23 | **59 cuts** | Mirror-flat turquoise water, long speed passes, kite showcases. |
| **`[AI SELECTS] Drone - Hurghada`** | 53 | **101 cuts** | Sandbars, kiteloops, fast transitions, and wide vistas. |
| **`[AI SELECTS] Drone - Sokhna`** | 70 | **114 cuts** | High-energy carving turns, spray impacts, low-altitude chases. |
| **Total** | **146 clips** | **274 selects** | **15.9 minutes of pre-trimmed highlights (Runtime: ~10.8 min)** |

---

## 3. VEGAS Pro 2026 Automation & Scripting Suite

### Import AI Selects (`ImportAISelects.cs`)
Located at **`Tools -> Scripting -> Import AI Selects`** inside VEGAS Pro:

```
[Import AI Selects Dialog]
• Click YES    ──► Replaces previous AI Selects tracks with fresh cuts
• Click NO     ──► Appends new cuts to the end of existing tracks
• Click CANCEL ──► Aborts without modifying anything
(Your rough cut tracks are 100% protected and never touched)
```

#### Key Capabilities:
* **Multi-Track Auto-Generation**: Reads `track_name` metadata from the manifest and dynamically generates separate tracks for each location/category.
* **Timeline Markers**: Creates named markers (`[DAHAB PROMO] ...`, `[SOKHNA PROMO] ...`) at every event start point for instant scrubbing.
* **Unicode & Path Resilience**: Automatically resolves special characters (e.g., `drone\uf028`) using UTF-8 decoding and fallback path unescaping.
* **Safe Offset Alignment**: Clips are placed with exact `SourceInMs` offsets into native video streams.

---

### The Complete 14-Plugin Suite

All scripts are written in C# and compiled dynamically by VEGAS Pro's internal Roslyn / .NET scripting engine:

| Script Filename | VEGAS Menu Label | Function & Editorial Purpose |
| :--- | :--- | :--- |
| **`ImportAISelects.cs`** | `Import AI Selects` | Loads AI Scout manifests, constructs multi-track selects reels with action markers. |
| **`SendToResolve.cs`** | `Send to DaVinci Resolve` | Exports active timeline (clips, tracks, markers, mute, speed, pan/crop) to Live Link bridge. |
| **`ReceiveFromResolve.cs`** | `Receive from DaVinci Resolve` | Re-imports color-graded timeline from DaVinci Resolve back into VEGAS Pro. |
| **`AutoSpeedRamp.cs`** | `Auto Speed Ramp` | Applies dynamic velocity ramps (100% → 300% → 50% slow-mo) to selected clips. |
| **`ImpactSnapZoom.cs`** | `Impact Snap Zoom` | Adds an instant 120% keyframed snap-zoom with smooth return at action moments. |
| **`AutoExposureFix.cs`** | `Auto Exposure Fix` | Automatically adds Color Corrector FX to lift underexposed action footage. |
| **`BatchFlashTransitions.cs`** | `Batch Flash Transitions` | Injects 4-frame white flash / cross-dissolve transitions across all selected cut points. |
| **`BatchAudioFades.cs`** | `Batch Audio Fades` | Applies 50ms anti-pop micro-fades to audio event boundaries. |
| **`ColorCodeFootage.cs`** | `Color Code Footage` | Color-codes timeline event clips by resolution, frame rate, or camera type. |
| **`CloseTimelineGaps.cs`** | `Close Timeline Gaps` | Ripple-closes all blank spaces between clips on selected tracks. |
| **`ClearMarkers.cs`** | `Clear All Markers` | Cleans up temporary or old scout markers from the ruler. |
| **`CleanMediaPool.cs`** | `Clean Media Pool` | Purges unused clips from the Project Media pool to reduce file size. |
| **`ToggleProxies.cs`** | `Toggle Proxies vs RAW` | 1-click swap between lightweight proxy files and native 4K/6K RAW masters. |
| **`RenderRegionsAsClips.cs`** | `Render Regions as Clips` | Batch renders timeline regions as standalone clips using current render template. |

---

## 4. Live Link & Bidirectional Synchronization

The Live Link bridge eliminates the need to export intermediate FCPXML or EDL files when moving between VEGAS Pro and DaVinci Resolve Studio.

```
┌──────────────┐                               ┌──────────────────────┐
│  VEGAS Pro   │  Tools -> Scripting           │  DaVinci Resolve     │
│  (2026/23)   ├─────────────────────────────► │  Studio (21/20/19)   │
│              │  ~/.timeline_bridge/          │  Workspace -> Scripts│
│              │  vegas_timeline.json          │                      │
│              │ ◄─────────────────────────────┤                      │
└──────────────┘  resolve_timeline.json        └──────────────────────┘
```

### Data Preserved Across NLEs:
* **Zero-Gap Source Alignment**: Converts millisecond timecodes to exact source-media frame counts to prevent 1-frame drift.
* **Pan/Crop & Transform Sync**: Translates VEGAS Pan/Crop zoom ($X, Y$ scale) and rotation degrees into Resolve's Timeline Item properties.
* **Track Hierarchy & Mute State**: Preserves video/audio track order and muted/unmuted statuses.
* **Playback Velocity**: Translates VEGAS velocity envelopes and clip playback rates into Resolve speed multipliers.
* **Timeline Markers & Regions**: Color and text labels transfer bidirectionally.

---

## 5. FastMCP Server (AI Assistant Integration)

The project includes an official **Model Context Protocol (FastMCP)** server (`vegas_mcp/server.py`), allowing LLMs to directly read and operate the timeline:

### Tools Exposed to LLMs:
1. `vegas_get_timeline_info()`: Reads active VEGAS project name, frame rate, resolution, track layout, clip counts, and markers.
2. `vegas_scout_footage(folder_path, target_duration_s)`: Runs visual motion scout on any directory and returns detected segments.
3. `vegas_get_selects_manifest()`: Reads the current selects manifest from disk.
4. `vegas_sync_to_resolve()`: Triggers background synchronization into DaVinci Resolve Studio.
5. `resolve_get_project_info()`: Checks Resolve connection status, active project, and active timeline.
6. `resolve_sync_to_vegas()`: Triggers export from Resolve back to VEGAS.

### Configuration for Claude Desktop / Antigravity
Add to `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "vegas-resolve": {
      "command": "python",
      "args": ["C:\\Users\\Mi5a\\VegasDavinciLinkTool\\run_mcp.py"]
    }
  }
}
```

---

## 6. XML Cleaner & Standalone Desktop GUI

For workflows where XML exchange is specifically required, the repository includes a Python-powered XML sanitization engine (`core/xml_cleaner.py`) and a desktop application (`gui/app.py`).

### Sanitization Pipeline:
1. **URI Normalization**: Converts Windows paths (`C:\Media\clip.mp4`) to standard URIs (`file://localhost/C:/Media/clip.mp4`) and vice versa.
2. **Proprietary Metadata Scrubbing**: Strips non-standard XML tags injected by VEGAS (`<trackmotion>`, `<pan>`, `<magixfx>`) that cause Resolve import crashes.
3. **Framerate Healing**: Ensures every `<rate>` tag specifies matching `<timebase>` and `<ntsc>` flags.
4. **Empty Track Pruning**: Removes orphan tracks that lack clips.

---

## 7. Step-by-Step Operator Manual

### A. How to Run AI Scout on New Footage
1. Open a terminal in the project directory:
   ```powershell
   python run_drone_scout.py
   ```
2. Or scan any custom footage directory directly:
   ```python
   from core.ai_scout import scout_directory, export_selects_manifest

   selects = scout_directory(
       directory_path=r"D:\MyProject\Footage",
       target_duration_s=3.5,
       track_name="[AI SELECTS] Action Highlights"
   )
   export_selects_manifest(selects)
   ```

### B. How to Import Selects in VEGAS Pro 2026
1. Open **VEGAS Pro 2026**.
2. Open your active project or create a new timeline.
3. In the top menu, navigate to:
   **`Tools` ➔ `Scripting` ➔ `Import AI Selects`**.
4. When prompted:
   * Select **YES** to replace previous AI select tracks with the fresh cuts.
   * Select **NO** to append cuts to the end of the existing tracks.
5. Review the imported tracks (`Dahab`, `Hurghada`, `Sokhna`) and scrub using the auto-generated action markers.

### C. How to Roundtrip to DaVinci Resolve Studio for Color Grading
1. Complete your picture lock / rough cut in **VEGAS Pro 2026**.
2. Click **`Tools` ➔ `Scripting` ➔ `Send to DaVinci Resolve`**.
3. Open **DaVinci Resolve Studio**.
4. In Resolve, go to:
   **`Workspace` ➔ `Scripts` ➔ `ImportFromVegas`**.
5. Grade your timeline using Resolve’s Color page.
6. When finished, run **`Workspace` ➔ `Scripts` ➔ `ExportToVegas`** in Resolve.
7. Back in VEGAS Pro 2026, click **`Tools` ➔ `Scripting` ➔ `Receive from DaVinci Resolve`** to load the graded cut.

---

*Master documentation compiled for **VegasDavinciLinkTool** — Main Branch.*
