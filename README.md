<p align="center">
  <h1 align="center">🎬 Vegas ↔ DaVinci Resolve Timeline Bridge</h1>
  <p align="center">
    <strong>Cut in Vegas. Grade in Resolve. No broken timelines.</strong>
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-what-it-does">What It Does</a> •
    <a href="#-how-to-use">How to Use</a> •
    <a href="#-features">Features</a> •
    <a href="#-faq">FAQ</a>
  </p>
</p>

---

## 😤 The Problem

You edited a project in **VEGAS Pro**, exported the timeline as an XML, and tried to import it into **DaVinci Resolve** for color grading. What happened?

- ❌ **"Media Offline"** — Resolve can't find your files because VEGAS wrote Windows paths (`D:\Footage\Clip.mp4`) instead of proper file URIs (`file://localhost/D:/Footage/Clip.mp4`)
- ❌ **Import crashes or silent failures** — VEGAS injects proprietary effect metadata (Track Motion, Pan/Crop, MAGIX Video FX) that Resolve's XML parser chokes on
- ❌ **Mismatched framerates** — Some clips are missing `<rate>` tags, causing Resolve to guess wrong and shift your edit
- ❌ **Empty ghost tracks** cluttering up Resolve's timeline

Going the other way is just as bad — Resolve exports `file://localhost/` URIs that VEGAS can't read, triggering the dreaded **"Search for Missing Files"** dialog on every clip.

## ✅ The Solution

**Timeline Bridge** provides complete synchronization and AI-assisted editorial workflows between VEGAS Pro and DaVinci Resolve:
1. **⚡ Direct Live Link (No XML Needed)**: In-app plugins for VEGAS Pro and DaVinci Resolve that stream cuts, tracks, and media bidirectionally with one click.
2. **🤖 Official Model Context Protocol (MCP) Server**: Connects LLMs (Claude Desktop, Antigravity, Cursor) directly to VEGAS Pro and DaVinci Resolve to inspect timelines, trigger syncs, and scout footage using AI.
3. **🏄 AI Visual & Motion Action Scout**: Scans hours of raw/proxy footage using hardware-accelerated frame analysis to isolate peak action moments (jumps, kiteloops, water spray, carves) and drops them pre-trimmed onto your VEGAS timeline as an `[AI SELECTS]` track with markers.
4. **📁 XML Sanitizer**: Drop in your exported XML, hit Convert, and get a clean Final Cut Pro XML v4/v5 that imports into either NLE without media offline or timecode errors.

**Zero paid dependencies. Zero telemetry. Works 100% offline.**

---

## 🤖 VEGAS Pro & DaVinci Resolve MCP Server

The first open-source Model Context Protocol server enabling AI assistants (such as Claude Desktop, Cursor, and Antigravity) to understand and control professional NLE editing workflows.

### Claude Desktop Setup
Add this to your `claude_desktop_config.json` (located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "vegas-resolve": {
      "command": "python",
      "args": [
        "C:\\Users\\Mi5a\\VegasDavinciLinkTool\\run_mcp.py"
      ]
    }
  }
}
```

### Available MCP Tools:
| Tool Name | Description |
| :--- | :--- |
| `vegas_get_timeline_info` | Reads track hierarchy, clip counts, markers, frame rate, and dimensions from VEGAS Pro. |
| `vegas_scout_footage` | Scans raw/proxy footage directories using motion analysis to detect peak action moments. |
| `vegas_get_selects_manifest` | Inspects pre-trimmed AI action selects with start/duration timestamps. |
| `vegas_sync_to_resolve` | Executes live background sync of active VEGAS project into DaVinci Resolve Studio. |
| `resolve_sync_to_vegas` | Exports active DaVinci Resolve Studio timeline for import into VEGAS Pro. |
| `resolve_get_project_info` | Checks DaVinci Resolve connection status, active project, and active timeline name. |

---

## 🏄 AI Visual & Motion Action Scout

Tired of scrubbing through hundreds of gigabytes of raw drone and camera footage to find 3-second action highlights?

1. **Hardware-Accelerated Frame Sampling**: Scans clips using parallel FFmpeg workers and keyframe decoding (10x–20x faster than real-time playback).
2. **Peak Motion Delta Detection**: Computes motion energy gradients to pinpoint exact jumps, kiteloops, speed bursts, and spray turns.
3. **Pacing-Matched Selects**: Automatically pre-trims each peak to 1.5s–3.0s matching fast-paced action promo pacing.
4. **1-Click VEGAS Pro Import**: Run **Tools → Scripting → Import AI Selects** in VEGAS Pro to instantly build an `[AI SELECTS] Kiting Action` track above your rough cut with labeled markers!

---

## ⚡ Direct Live Link (Bidirectional Plugins)

Connects **VEGAS Pro** (2026.0, 23.0, 22.0, 21.0) and **DaVinci Resolve Studio** (21 / 20 / 19) directly without manual file exporting:

### 1-Minute Setup
Double-click `install_plugins.bat` to automatically install the full 14-script automation suite:
- **VEGAS Pro**: Installs into `Tools → Scripting` across all versions (2026.0, 23.0, 22.0, 21.0, 20.0).
- **DaVinci Resolve**: Installs `ImportFromVegas` and `ExportToVegas` into `Workspace → Scripts`.

---

## 🛠️ VEGAS Pro Power Editing & Automation Suite

Every script runs natively inside VEGAS Pro via **Tools → Scripting** with zero external dependencies:

| Script Name | Menu Item | Description |
| :--- | :--- | :--- |
| `ToggleProxies.cs` | **Toggle Proxies vs RAW** | 1-Click toggle between `Proxy\file.mov` and native 4K/6K RAW files in parent folder. |
| `CloseTimelineGaps.cs` | **Close Timeline Gaps** | Ripple gap closer: eliminates all black gaps and dead air across selected or all tracks. |
| `AutoExposureFix.cs` | **Auto Exposure Fix** | Automatically balances exposure: lifts crushed shadows & tames blown sea/sky highlights. |
| `AutoSpeedRamp.cs` | **Auto Speed Ramp** | Injects high-energy action speed ramp (300% entry $\rightarrow$ 40% slow-mo trick $\rightarrow$ 100% landing). |
| `ImpactSnapZoom.cs` | **Impact Snap Zoom** | 6-frame 114% punch-in snap zoom on trick landings and bass drops via Pan/Crop keyframes. |
| `BatchFlashTransitions.cs`| **Batch Flash Transitions** | Inserts 6-frame white flash or high-energy fast-cut transitions across adjacent clips. |
| `BatchAudioFades.cs` | **Batch Audio Fades** | Injects 10ms anti-pop / click micro-fades to heads and tails of all audio cuts. |
| `ColorCodeFootage.cs` | **Color Code Footage** | Classifies and tags clips by frame rate (120fps slow-mo, 60fps sports, 24fps cinema). |
| `CleanMediaPool.cs` | **Clean Media Pool** | Purges all unused media files from the `.veg` project to maximize stability and speed. |
| `RenderRegionsAsClips.cs` | **Render Regions as Clips** | Batch renders each timeline region into an individual video file named after the region. |
| `ClearMarkers.cs` | **Clear All Markers** | 1-Click clean up dialog to purge all markers and regions from the active timeline. |
| `ImportAISelects.cs` | **Import AI Selects** | Imports AI-scouted highlight cuts onto organized, stacked timeline tracks. |
| `SendToResolve.cs` | **Send to DaVinci Resolve** | 1-Click live bridge export to DaVinci Resolve Studio. |
| `ReceiveFromResolve.cs` | **Receive from DaVinci Resolve** | 1-Click live bridge import back to VEGAS Pro. |

---

### What Gets Transferred:
- ✅ **All Video & Audio Track Layers**: Full track hierarchy, naming, and order.
- ✅ **Cuts, Trims, & In/Outs**: Exact millisecond and frame-level cut points.
- ✅ **Zero-Gap Media FPS Scaling**: Mixed frame rates (e.g. 59.94 fps Sony/DJI clips on a 29.97 fps timeline) automatically scaled with **0.00 frame gaps**.
- ✅ **Automatic Media Re-linking**: Media Pool items are matched and ingested with `Start TC` aligned to `00:00:00:00` (eliminating "timecode extents do not match").
- ✅ **Timeline Markers & Regions**: VEGAS markers become Resolve Cyan timeline markers; VEGAS regions become Yellow duration markers.
- ✅ **Track Mute & Solo**: Track states mirrored directly.
- ✅ **Clip Retime & Speed**: Playback velocity (slow-motion / fast-forward) scaled to Resolve cuts.
- ✅ **Track Volume (dB) & Pan**: Audio mixer parameters extracted.

---

### Workflow 1: VEGAS Pro → DaVinci Resolve
1. In VEGAS Pro: Go to **Tools → Scripting → Send to DaVinci Resolve**.
2. **Instant Sync**: The bridge automatically creates and populates your timeline inside DaVinci Resolve with zero gaps and all media online!
   *(Or click **🔗 Sync VEGAS → Resolve** inside the desktop app).*

### Workflow 2: DaVinci Resolve → VEGAS Pro (Round-Trip)
1. In DaVinci Resolve: Go to **Workspace → Scripts → ExportToVegas**.
2. In VEGAS Pro: Go to **Tools → Scripting → Receive from DaVinci Resolve**.
3. Your timeline in VEGAS Pro is updated with the graded cuts!
   *(Or click **🔄 Sync Resolve → VEGAS** inside the desktop app).*

---

## 📊 Supported Versions & Compatibility

| NLE Platform | Version Range | Live Link (1-Click Auto) | In-App Script Menu | XML Sanitizer Engine |
| :--- | :--- | :---: | :---: | :---: |
| **VEGAS Pro** | **2026.0, 23.0, 22.0, 21.0, 20.0** | ✅ **Full Auto** | ✅ **Supported** | ✅ **Universal** |
| **VEGAS Pro** | **19.0, 18.0, 17.0, 16.0, 15.0, 14.0** | ✅ **Full Auto** | ✅ **Supported** | ✅ **Universal** |
| **Sony Vegas (Legacy)** | **13.0, 12.0, 11.0, 10.0** | ⚠️ *Via XML* | ⚠️ *Via XML* | ✅ **Universal** |
| **DaVinci Resolve Studio** | **Resolve 21, 20, 19, 18, 17, 16, 15** | ✅ **Full Auto** | ✅ **Supported** | ✅ **Universal** |
| **DaVinci Resolve Free** | **Resolve 21, 20, 19, 18, 17, 16** | ⚠️ *(In-App/XML)* | ✅ **Supported** | ✅ **Universal** |

### Compatibility Details:
- **VEGAS Pro (14.0 up to 2026.0)**: Uses the official `ScriptPortal.Vegas` .NET API. `install_plugins.bat` automatically scans your computer and installs the scripts into every installed VEGAS version simultaneously.
- **DaVinci Resolve Studio (15 to 21)**: Full automatic background synchronization via Blackmagic's official `DaVinciResolveScript` API. Clicking "Send to DaVinci Resolve" in VEGAS updates Resolve automatically without switching apps.
- **DaVinci Resolve Free Edition**: Blackmagic officially restricts external background API connections on the Free version. Free edition users can either run **Workspace → Scripts → ImportFromVegas** directly inside Resolve, or use the Desktop App's XML Sanitizer.
- **Legacy Sony Vegas (13 and older)**: Supported 100% via the Universal XML Sanitizer engine, which processes Final Cut Pro XML v4/v5 files back to Vegas Pro 7.

---




## 📥 Installation

### Step 1: Install Python (if you don't have it)

You need **Python 3.8 or newer**. Most editors don't have this yet — here's how to get it:

<details>
<summary><strong>🪟 Windows (most common for Vegas editors)</strong></summary>

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow **"Download Python 3.x.x"** button
3. Run the installer
4. **⚠️ IMPORTANT: Check the box that says "Add Python to PATH"** at the bottom of the installer — this is the #1 mistake people make
5. Click "Install Now"
6. To verify, open **Command Prompt** or **PowerShell** and type:
   ```
   python --version
   ```
   You should see something like `Python 3.12.x`

</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

1. Open **Terminal** (press `Cmd + Space`, type "Terminal")
2. Install via Homebrew (recommended):
   ```bash
   brew install python
   ```
   Or download from [python.org/downloads](https://www.python.org/downloads/)
3. Verify:
   ```bash
   python3 --version
   ```

</details>

<details>
<summary><strong>🐧 Linux</strong></summary>

Python is usually pre-installed. Check with:
```bash
python3 --version
```
If not installed:
```bash
# Ubuntu/Debian
sudo apt install python3

# Fedora
sudo dnf install python3
```

</details>

### Step 2: Download the Tool

**Option A — With Git (recommended)**

If you have Git installed ([download Git here](https://git-scm.com/downloads) if not):

```bash
git clone https://github.com/michaelmagdy15/VegasDavinciLinkToolz.git
cd VegasDavinciLinkToolz
```

**Option B — Direct Download (no Git needed)**

1. Go to [github.com/michaelmagdy15/VegasDavinciLinkToolz](https://github.com/michaelmagdy15/VegasDavinciLinkToolz)
2. Click the green **"Code"** button → **"Download ZIP"**
3. Extract the ZIP wherever you want (e.g., your Desktop)
4. Open a terminal in the extracted folder

### Step 3: Launch the App

**On Windows:**
- Simply double-click **`launch.bat`** in the folder!
- *Bonus:* You can even **drag and drop** your XML file directly onto `launch.bat` to launch with it preloaded.

**On macOS / Linux:**
```bash
./launch.sh
```

**Or via Terminal / Command Prompt:**
```bash
python main.py
```

> **Note for macOS/Linux users:** If `python` doesn't work, try `python3 main.py` or `./launch.sh` instead.

That's it — the GUI opens and you're ready to convert. No `pip install`, no virtual environments, no setup wizards.

---

## 🚀 Quick Start (TL;DR)

**GUI Mode:**
```bash
git clone https://github.com/michaelmagdy15/VegasDavinciLinkToolz.git
cd VegasDavinciLinkToolz
python main.py
```
Or double-click **`launch.bat`**.

**CLI / Automation Mode:**
Need to batch-convert or automate inside scripts? Run headless without the GUI:
```bash
# Convert Vegas XML for DaVinci Resolve
python main.py timeline.xml --cli

# Convert Resolve XML back for Vegas Pro
python main.py graded.xml --cli -m resolve_to_vegas

# Convert with path remapping and custom output path
python main.py timeline.xml --cli --remap-src "D:/Projects" --remap-dst "E:/Media" -o converted.xml
```

---

## 🔧 What It Does

### Vegas → Resolve (the main workflow)

| Step | What Gets Fixed |
|---|---|
| **Path Conversion** | `D:\Footage\My Clip.mp4` → `file://localhost/D:/Footage/My%20Clip.mp4` |
| **URL Encoding** | Spaces, parentheses, special chars get RFC 3986 encoded |
| **Effect Stripping** | Removes VEGAS/Sony/MAGIX proprietary effects that crash Resolve |
| **Safe Effect Preservation** | Keeps standard FCP7 effects Resolve understands (Opacity, Basic Motion, Audio Levels, Cross Dissolve) |
| **Timecode Normalization** | Ensures consistent framerate tags across every clip and track |
| **A/V Sync** | All `<link>` tags (audio-video sync references) are 100% preserved |
| **Empty Track Cleanup** | Removes empty placeholder tracks VEGAS exports |

### Resolve → Vegas (bringing it back)

| Step | What Gets Fixed |
|---|---|
| **URI → Windows Path** | `file://localhost/D:/Footage/My%20Clip.mp4` → `D:\Footage\My Clip.mp4` |
| **URL Decoding** | `%20` → spaces, `%28` → parentheses, etc. |
| **A/V Sync** | Link tags preserved |

### Batch Path Remapping (both directions)

Moved your footage to a new drive? Changed your folder structure? Use the **Path Remapping** fields:

```
Find:    C:\OldProjects\Wedding\
Replace: E:\Media\Wedding\
```

Every matching path in the XML gets updated. Works with both Windows paths and file URIs.

---

## 📖 How to Use

### 1. Export from VEGAS Pro

In VEGAS Pro 2026:
1. Go to **File → Export → Final Cut Pro XML** (or **File → Render As** and choose XML)
2. Save the `.xml` file somewhere accessible

### 2. Run Timeline Bridge

```bash
python main.py
```

### 3. Convert

1. **Select mode**: "Vegas Pro → DaVinci Resolve" (default)
2. **Browse** to your exported XML file
3. *(Optional)* Enter path remapping if your footage moved
4. Click **⚡ Convert Timeline**
5. Watch the log — it shows every path fixed, every effect stripped
6. Output file is saved next to your input as `yourfile_for_resolve.xml`

### 4. Import into Resolve

In DaVinci Resolve Studio 21:
1. Go to **File → Import → Timeline → Import AAF, EDL, XML...**
2. Select the `_for_resolve.xml` file
3. Your timeline imports cleanly — all cuts, clips, and A/V sync intact

### 5. Going Back (Optional)

After grading in Resolve:
1. **File → Export → Timeline → FCP 7 XML**
2. Run Timeline Bridge in **"Resolve → Vegas"** mode
3. Import the `_for_vegas.xml` back into VEGAS Pro — no missing files

---

## ✨ Features

- 🎯 **One-click conversion** — no command line needed
- 🖥️ **Dark-themed GUI** — looks at home next to Resolve and Vegas
- 📋 **Real-time log** — see exactly what's being fixed
- 🔄 **Bidirectional** — Vegas→Resolve AND Resolve→Vegas
- 📁 **Batch path remapping** — fix drive letters and folder moves
- 🛡️ **Safe effect whitelist** — only strips what Resolve can't read
- ⏱️ **Timecode normalization** — no more framerate mismatches
- 🔗 **A/V sync preservation** — link tags never touched
- 🧹 **Empty track cleanup** — clean timeline in Resolve
- 📦 **Zero dependencies** — pure Python stdlib, runs anywhere
- 💰 **100% free and open source** — MIT license

---

## 🧪 Running Tests

```bash
# From the project root
python -m pytest tests/ -v
```

Tests cover:
- Path conversion (Windows ↔ file URI) with edge cases (spaces, unicode, parentheses)
- Effect stripping whitelist accuracy
- Timecode normalization
- Full round-trip: Vegas XML → Resolve XML → Vegas XML
- Link tag preservation

---

## 📁 Project Structure

```
VegasDavinciLinkToolz/
├── main.py                  # Launch the app
├── gui/
│   ├── app.py               # Main window (Tkinter)
│   └── widgets.py           # Reusable UI components
├── core/
│   ├── parser.py            # XMEML XML parser
│   ├── path_sanitizer.py    # Windows ↔ file:// URI conversion
│   ├── xml_cleaner.py       # Effect stripping & timecode fixing
│   └── converter.py         # Orchestrator (ties it all together)
├── tests/
│   ├── test_path_sanitizer.py
│   ├── test_xml_cleaner.py
│   ├── test_converter.py
│   └── fixtures/
│       ├── vegas_sample.xml     # Simulated VEGAS export (with issues)
│       └── resolve_sample.xml   # Simulated Resolve export
├── requirements.txt         # (empty — stdlib only!)
└── .gitignore
```

---

## ❓ FAQ

**Q: Does this work with VEGAS Pro versions other than 2026?**
A: Yes! The XML format (XMEML / FCP7 XML) hasn't changed significantly across VEGAS versions. Should work with VEGAS Pro 14+.

**Q: Does this work with free DaVinci Resolve (not Studio)?**
A: Yes, both free Resolve and Resolve Studio use the same XML import.

**Q: Will I lose my edits/cuts?**
A: No. The tool only modifies file paths, strips incompatible effects, and normalizes timecodes. Your actual edit (in/out points, clip positions, track layout, A/V sync) is never changed.

**Q: What about transitions?**
A: Standard transitions (Cross Dissolve, Fade In/Out, Dip to Color) are preserved. VEGAS-only transitions may need to be re-applied in Resolve.

**Q: Can I use this with Premiere Pro or Final Cut?**
A: The tool is optimized for the Vegas↔Resolve workflow, but since it outputs clean FCP7 XML, the output should be compatible with any NLE that reads that format.

**Q: Do I need to install anything?**
A: Just Python 3.8+. No pip packages, no Node.js, no Docker. Download Python from [python.org](https://www.python.org/downloads/) if you don't have it.

---

## 🤝 Contributing

Found a bug? Have a feature idea? PRs are welcome!

1. Fork the repo
2. Create a branch (`git checkout -b fix/my-fix`)
3. Make your changes
4. Run tests (`python -m pytest tests/ -v`)
5. Open a PR

---

## 📄 License

MIT License — use it however you want, free forever.

---

<p align="center">
  <strong>Built for editors, by editors.</strong><br>
  <em>Because your timeline shouldn't break just because you switched apps.</em>
</p>
