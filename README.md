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

**Timeline Bridge** provides two ways to synchronize your projects:
1. **⚡ Direct Live Link (No XML Needed)**: Direct in-app plugins for VEGAS Pro and DaVinci Resolve that stream cuts, tracks, and media bidirectionally with one click.
2. **📁 XML Sanitizer**: Drop in your exported XML, hit Convert, and get a clean file that imports into either NLE without media offline or timecode errors.

**Zero dependencies. Zero cost. Zero internet required.**

---

## ⚡ Direct Live Link (Bidirectional Plugins)

Connects VEGAS Pro (2026.0, 23.0, 22.0) and DaVinci Resolve Studio (21 / 20 / 19) directly without manual file exporting:

### 1-Minute Setup
Double-click `install_plugins.bat` to automatically install the plugins into:
- VEGAS Pro: `Tools → Scripting`
- DaVinci Resolve: `Workspace → Scripts`

### Workflow 1: VEGAS Pro → DaVinci Resolve
1. In VEGAS Pro: Go to **Tools → Scripting → Send to DaVinci Resolve**.
2. Inside Resolve: The timeline is built automatically with 100% online media and zero gaps! (Or run **Workspace → Scripts → ImportFromVegas**).

### Workflow 2: DaVinci Resolve → VEGAS Pro
1. In DaVinci Resolve: Go to **Workspace → Scripts → ExportToVegas**.
2. In VEGAS Pro: Go to **Tools → Scripting → Receive from DaVinci Resolve**.
3. All cuts, grades-ready clips, and audio tracks sync back into VEGAS Pro!

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
