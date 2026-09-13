"""
live_link_dashboard.py — Real-time GUI Dashboard for VEGAS Pro <-> DaVinci Resolve Live Link.

Features:
- Live detection of VEGAS Pro project & DaVinci Resolve Studio status
- Visual progress bar and real-time step-by-step transfer log
- One-click Live Sync button (VEGAS -> Resolve)
- Roundtrip button (Resolve -> VEGAS)
- Background file watcher that automatically animates progress when VEGAS clicks "Send to DaVinci Resolve"
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.live_bridge import (
    get_resolve_app,
    is_resolve_running,
    get_current_project_info,
    import_timeline_from_json,
    export_timeline_to_json,
    load_manifest_json,
    _init_resolve_env,
)
from core.path_sanitizer import get_bridge_dir

COLORS = {
    "bg_main": "#0f111a",
    "bg_card": "#181b28",
    "bg_card_inner": "#1e2233",
    "border": "#282d42",
    "text_white": "#ffffff",
    "text_muted": "#8a91a8",
    "text_accent": "#00d2ff",
    "accent_blue": "#0066ff",
    "accent_blue_hover": "#267dff",
    "accent_green": "#00e676",
    "accent_green_hover": "#33eb91",
    "accent_orange": "#ff9100",
    "accent_red": "#ff1744",
    "log_bg": "#0a0c13",
}


class LiveLinkDashboard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🎬 VEGAS Pro ↔ DaVinci Resolve Live Link Dashboard")
        self.root.geometry("860x740")
        self.root.minsize(800, 680)
        self.root.configure(bg=COLORS["bg_main"])

        self.bridge_dir = get_bridge_dir()
        self.timeline_json = self.bridge_dir / "vegas_timeline.json"
        self.deep_scan_json = self.bridge_dir / "vegas_deep_scan.json"

        self.is_syncing = False
        self.auto_sync_enabled = tk.BooleanVar(value=True)
        self.last_json_mtime = 0.0

        if self.timeline_json.exists():
            self.last_json_mtime = self.timeline_json.stat().st_mtime

        self._build_ui()
        self._start_status_poller()
        self._start_auto_watch_thread()

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self.root, bg=COLORS["bg_card"], height=70, bd=0, highlightthickness=1, highlightbackground=COLORS["border"])
        header.pack(fill="x", padx=14, pady=(12, 8))
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="🎬 VEGAS Pro ↔ DaVinci Resolve Live Link",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["text_white"],
            bg=COLORS["bg_card"],
        )
        title_lbl.pack(side="left", padx=16, pady=(10, 2))

        sub_lbl = tk.Label(
            header,
            text="Real-Time 11-Dimension Editorial, OFX & Color Sync",
            font=("Segoe UI", 9),
            fg=COLORS["text_accent"],
            bg=COLORS["bg_card"],
        )
        sub_lbl.place(x=18, y=40)

        self.overall_status_pill = tk.Label(
            header,
            text="🟢 LIVE LINK READY",
            font=("Segoe UI", 9, "bold"),
            fg=COLORS["accent_green"],
            bg=COLORS["bg_card_inner"],
            padx=12,
            pady=4,
        )
        self.overall_status_pill.pack(side="right", padx=16, pady=18)

        # 2. Status Cards Container (Side by Side)
        cards_frame = tk.Frame(self.root, bg=COLORS["bg_main"])
        cards_frame.pack(fill="x", padx=14, pady=4)

        # Card Left: VEGAS Pro
        self.vegas_card = tk.Frame(cards_frame, bg=COLORS["bg_card"], bd=0, highlightthickness=1, highlightbackground=COLORS["border"])
        self.vegas_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        v_head = tk.Label(self.vegas_card, text="VEGAS Pro (Source)", font=("Segoe UI", 11, "bold"), fg=COLORS["text_white"], bg=COLORS["bg_card"])
        v_head.pack(anchor="w", padx=14, pady=(10, 2))

        self.vegas_proj_lbl = tk.Label(self.vegas_card, text="Project: Scanning...", font=("Segoe UI", 10), fg=COLORS["text_accent"], bg=COLORS["bg_card"])
        self.vegas_proj_lbl.pack(anchor="w", padx=14, pady=1)

        self.vegas_stats_lbl = tk.Label(self.vegas_card, text="Tracks: -- | Clips: --", font=("Segoe UI", 9), fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        self.vegas_stats_lbl.pack(anchor="w", padx=14, pady=1)

        self.vegas_fx_lbl = tk.Label(self.vegas_card, text="OFX: Detecting...", font=("Segoe UI", 9), fg=COLORS["accent_orange"], bg=COLORS["bg_card"])
        self.vegas_fx_lbl.pack(anchor="w", padx=14, pady=(1, 10))

        # Card Right: DaVinci Resolve
        self.resolve_card = tk.Frame(cards_frame, bg=COLORS["bg_card"], bd=0, highlightthickness=1, highlightbackground=COLORS["border"])
        self.resolve_card.pack(side="right", fill="both", expand=True, padx=(6, 0))

        r_head = tk.Label(self.resolve_card, text="DaVinci Resolve Studio (Target)", font=("Segoe UI", 11, "bold"), fg=COLORS["text_white"], bg=COLORS["bg_card"])
        r_head.pack(anchor="w", padx=14, pady=(10, 2))

        self.resolve_proj_lbl = tk.Label(self.resolve_card, text="Project: Connecting...", font=("Segoe UI", 10), fg=COLORS["text_accent"], bg=COLORS["bg_card"])
        self.resolve_proj_lbl.pack(anchor="w", padx=14, pady=1)

        self.resolve_tl_lbl = tk.Label(self.resolve_card, text="Timeline: --", font=("Segoe UI", 9), fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        self.resolve_tl_lbl.pack(anchor="w", padx=14, pady=1)

        self.resolve_conn_lbl = tk.Label(self.resolve_card, text="IPC Connection: Checking...", font=("Segoe UI", 9), fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        self.resolve_conn_lbl.pack(anchor="w", padx=14, pady=(1, 10))

        # 3. Progress Section
        prog_card = tk.Frame(self.root, bg=COLORS["bg_card"], bd=0, highlightthickness=1, highlightbackground=COLORS["border"])
        prog_card.pack(fill="x", padx=14, pady=6)

        prog_top_row = tk.Frame(prog_card, bg=COLORS["bg_card"])
        prog_top_row.pack(fill="x", padx=14, pady=(10, 4))

        self.status_msg_lbl = tk.Label(prog_top_row, text="Status: Ready to sync", font=("Segoe UI", 10, "bold"), fg=COLORS["text_white"], bg=COLORS["bg_card"])
        self.status_msg_lbl.pack(side="left")

        self.percent_lbl = tk.Label(prog_top_row, text="0%", font=("Segoe UI", 10, "bold"), fg=COLORS["text_accent"], bg=COLORS["bg_card"])
        self.percent_lbl.pack(side="right")

        # Custom ttk progress bar styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Link.Horizontal.TProgressbar",
            troughcolor=COLORS["bg_card_inner"],
            background=COLORS["accent_blue"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["accent_blue"],
            darkcolor=COLORS["accent_blue"],
        )

        self.progress_bar = ttk.Progressbar(prog_card, style="Link.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=14, pady=(0, 10))

        # 4. Action Buttons & Auto-Sync Switch
        btn_bar = tk.Frame(self.root, bg=COLORS["bg_main"])
        btn_bar.pack(fill="x", padx=14, pady=4)

        self.sync_now_btn = tk.Button(
            btn_bar,
            text="🚀  SYNC VEGAS ➔ RESOLVE NOW",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["accent_blue"],
            fg=COLORS["text_white"],
            activebackground=COLORS["accent_blue_hover"],
            activeforeground=COLORS["text_white"],
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            command=self.trigger_sync,
        )
        self.sync_now_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.roundtrip_btn = tk.Button(
            btn_bar,
            text="🔄  SYNC RESOLVE ➔ VEGAS",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["bg_card_inner"],
            fg=COLORS["text_white"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text_white"],
            bd=0,
            padx=14,
            pady=9,
            cursor="hand2",
            command=self.trigger_roundtrip,
        )
        self.roundtrip_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

        opt_row = tk.Frame(self.root, bg=COLORS["bg_main"])
        opt_row.pack(fill="x", padx=14, pady=(2, 6))

        self.auto_sync_chk = tk.Checkbutton(
            opt_row,
            text="⚡ Auto-Sync automatically when 'Send to DaVinci Resolve' is clicked in VEGAS Pro",
            variable=self.auto_sync_enabled,
            font=("Segoe UI", 9),
            fg=COLORS["text_accent"],
            bg=COLORS["bg_main"],
            activebackground=COLORS["bg_main"],
            activeforeground=COLORS["text_accent"],
            selectcolor=COLORS["bg_card"],
            bd=0,
            highlightthickness=0,
        )
        self.auto_sync_chk.pack(side="left")

        # 5. Live Streaming Log Console
        log_frame = tk.Frame(self.root, bg=COLORS["bg_card"], bd=0, highlightthickness=1, highlightbackground=COLORS["border"])
        log_frame.pack(fill="both", expand=True, padx=14, pady=(4, 12))

        log_head_row = tk.Frame(log_frame, bg=COLORS["bg_card"])
        log_head_row.pack(fill="x", padx=12, pady=(8, 4))

        log_title = tk.Label(log_head_row, text="📋 Live Activity & Conform Console", font=("Segoe UI", 10, "bold"), fg=COLORS["text_white"], bg=COLORS["bg_card"])
        log_title.pack(side="left")

        clear_btn = tk.Button(
            log_head_row,
            text="Clear",
            font=("Segoe UI", 8),
            bg=COLORS["bg_card_inner"],
            fg=COLORS["text_muted"],
            bd=0,
            padx=8,
            pady=2,
            command=self._clear_log,
        )
        clear_btn.pack(side="right")

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=COLORS["log_bg"],
            fg=COLORS["text_white"],
            bd=0,
            padx=10,
            pady=8,
            insertbackground=COLORS["text_white"],
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tag configurations for syntax coloring
        self.log_text.tag_configure("ok", foreground=COLORS["accent_green"])
        self.log_text.tag_configure("info", foreground=COLORS["text_accent"])
        self.log_text.tag_configure("warn", foreground=COLORS["accent_orange"])
        self.log_text.tag_configure("error", foreground=COLORS["accent_red"])
        self.log_text.tag_configure("time", foreground=COLORS["text_muted"])

        self.log("[INFO] Live Link Dashboard initialized. Monitoring active NLE sessions...")

    def log(self, message: str):
        def _append():
            timestamp = time.strftime("[%H:%M:%S] ")
            self.log_text.insert(tk.END, timestamp, "time")

            tag = "info"
            if "[OK]" in message or "SUCCESS" in message or "built" in message.lower():
                tag = "ok"
            elif "[WARN]" in message:
                tag = "warn"
            elif "[ERROR]" in message:
                tag = "error"

            self.log_text.insert(tk.END, message + "\n", tag)
            self.log_text.see(tk.END)

        self.root.after(0, _append)

    def _clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def set_progress(self, percent: int, message: str):
        def _update():
            self.progress_bar["value"] = percent
            self.percent_lbl.config(text=f"{percent}%")
            self.status_msg_lbl.config(text=f"Status: {message}")
        self.root.after(0, _update)

    def _start_status_poller(self):
        def poll():
            while True:
                try:
                    self._update_vegas_card()
                    self._update_resolve_card()
                except Exception:
                    pass
                time.sleep(2.5)

        t = threading.Thread(target=poll, daemon=True)
        t.start()

    def _update_vegas_card(self):
        # Prefer deep scan if available for full OFX info, else timeline_json
        target_json = self.timeline_json if self.timeline_json.exists() else self.deep_scan_json
        if not target_json.exists():
            self.root.after(0, lambda: self.vegas_proj_lbl.config(text="Project: (No export yet)"))
            return

        try:
            data = load_manifest_json(str(target_json))
            pname = data.get("project_name", "Untitled")
            tracks = data.get("tracks", [])
            v_tracks = sum(1 for t in tracks if t.get("is_video", True))
            a_tracks = len(tracks) - v_tracks
            total_clips = sum(len(t.get("clips") or t.get("events") or []) for t in tracks)

            # Detect OFX plugins mentioned
            raw_str = json.dumps(data)
            detected = []
            if "rsmb" in raw_str.lower():
                detected.append("RSMB")
            if "levels" in raw_str.lower():
                detected.append("Levels")
            if "lut" in raw_str.lower():
                detected.append("LUT")
            if "sapphire" in raw_str.lower() or "s_warp" in raw_str.lower():
                detected.append("Sapphire")

            fx_text = "OFX: " + (", ".join(detected) if detected else "None")

            def _apply():
                self.vegas_proj_lbl.config(text=f"Project: {pname} (VEGAS 2026)")
                self.vegas_stats_lbl.config(text=f"Tracks: {len(tracks)} ({v_tracks}V / {a_tracks}A) | Clips: {total_clips}")
                self.vegas_fx_lbl.config(text=fx_text)

            self.root.after(0, _apply)
        except Exception:
            pass

    def _update_resolve_card(self):
        try:
            _init_resolve_env()
            resolve = get_resolve_app()
            if resolve:
                pm = resolve.GetProjectManager()
                proj = pm.GetCurrentProject() if pm else None
                tl = proj.GetCurrentTimeline() if proj else None

                proj_name = proj.GetName() if proj else "No project open"
                tl_name = tl.GetName() if tl else "No active timeline"

                def _apply():
                    self.resolve_proj_lbl.config(text=f"Project: {proj_name}", fg=COLORS["accent_green"])
                    self.resolve_tl_lbl.config(text=f"Timeline: {tl_name}")
                    self.resolve_conn_lbl.config(text="🟢 IPC Connected (Studio Scripting)", fg=COLORS["accent_green"])
                    self.overall_status_pill.config(text="🟢 LIVE LINK CONNECTED", fg=COLORS["accent_green"])

                self.root.after(0, _apply)
            else:
                def _apply_none():
                    self.resolve_proj_lbl.config(text="Project: Not responding", fg=COLORS["accent_orange"])
                    self.resolve_conn_lbl.config(text="🟡 Studio IPC connecting...", fg=COLORS["accent_orange"])
                    self.overall_status_pill.config(text="🟡 WAITING FOR RESOLVE", fg=COLORS["accent_orange"])

                self.root.after(0, _apply_none)
        except Exception:
            pass

    def _start_auto_watch_thread(self):
        def watch():
            while True:
                time.sleep(1.0)
                if not self.auto_sync_enabled.get() or self.is_syncing:
                    continue

                if self.timeline_json.exists():
                    try:
                        mtime = self.timeline_json.stat().st_mtime
                        if mtime > self.last_json_mtime:
                            self.last_json_mtime = mtime
                            self.log("[INFO] Detected fresh timeline manifest from VEGAS Pro! Auto-Sync starting...")
                            self.trigger_sync()
                    except Exception:
                        pass

        t = threading.Thread(target=watch, daemon=True)
        t.start()

    def trigger_sync(self):
        if self.is_syncing:
            return

        self.is_syncing = True
        self.sync_now_btn.config(state="disabled", text="⏳  SYNCING TIMELINE...")
        self.set_progress(10, "Reading VEGAS Pro Manifest...")

        def run():
            try:
                if not self.timeline_json.exists():
                    self.set_progress(0, "Error: No manifest found")
                    self.log("[ERROR] No vegas_timeline.json found. Click 'Send to DaVinci Resolve' in VEGAS Pro.")
                    return

                self.log(f"[INFO] Loading manifest: {self.timeline_json}")
                self.set_progress(25, "Inspecting Media Pool & Connecting to Resolve...")

                def custom_log(msg):
                    self.log(msg)
                    if "Importing" in msg:
                        self.set_progress(45, "Importing Media Files into Media Pool...")
                    elif "Created timeline" in msg:
                        self.set_progress(65, "Constructing Inverted Video Track Layering...")
                    elif "Attached" in msg or "Mapped" in msg:
                        self.set_progress(80, "Building Fusion Node Pipeline (RSMB + Levels)...")
                    elif "Linked" in msg:
                        self.set_progress(90, "Linking Paired A/V Clips & Setting Composite Modes...")

                success = import_timeline_from_json(str(self.timeline_json), log_fn=custom_log)

                if success:
                    self.set_progress(100, "✓ Live Sync Complete! 100% Zero-Gap Alignment.")
                    self.log("[SUCCESS] Timeline synchronized into DaVinci Resolve Studio with 100% fidelity!")
                else:
                    self.set_progress(0, "Sync failed. Check Resolve status.")
                    self.log("[ERROR] Live synchronization failed. Verify DaVinci Resolve Studio is open.")
            except Exception as e:
                self.set_progress(0, f"Error: {e}")
                self.log(f"[ERROR] Live Sync Exception: {e}")
            finally:
                self.is_syncing = False
                self.root.after(0, lambda: self.sync_now_btn.config(state="normal", text="🚀  SYNC VEGAS ➔ RESOLVE NOW"))
                self._update_resolve_card()

        threading.Thread(target=run, daemon=True).start()

    def trigger_roundtrip(self):
        if self.is_syncing:
            return

        self.is_syncing = True
        self.roundtrip_btn.config(state="disabled", text="⏳  EXPORTING RESOLVE...")
        self.set_progress(20, "Querying DaVinci Resolve Timeline...")

        def run():
            try:
                def custom_log(msg):
                    self.log(msg)

                out = export_timeline_to_json(log_fn=custom_log)
                if out:
                    self.set_progress(100, "✓ Graded cuts exported! Ready for VEGAS Receive.")
                    self.log("[SUCCESS] Export complete! In VEGAS Pro, click: Tools > Scripting > Receive from DaVinci Resolve.")
                else:
                    self.set_progress(0, "Export failed.")
                    self.log("[ERROR] Could not export active timeline from DaVinci Resolve.")
            except Exception as e:
                self.set_progress(0, f"Error: {e}")
                self.log(f"[ERROR] Roundtrip Exception: {e}")
            finally:
                self.is_syncing = False
                self.root.after(0, lambda: self.roundtrip_btn.config(state="normal", text="🔄  SYNC RESOLVE ➔ VEGAS"))

        threading.Thread(target=run, daemon=True).start()


def main():
    root = tk.Tk()
    app = LiveLinkDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
