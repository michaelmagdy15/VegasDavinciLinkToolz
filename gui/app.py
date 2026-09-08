"""
app.py — Main Tkinter application window for the Vegas ↔ Resolve Timeline Bridge.

Dark-themed, professional GUI that any editor can pick up:
  - Mode toggle (Vegas→Resolve / Resolve→Vegas)
  - File browser for input XML
  - Path remapping fields
  - Convert button with full logging
  - Status bar with summary
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional

from gui.widgets import (
    COLORS,
    LogPanel,
    StatusBar,
    SectionHeader,
    StyledEntry,
    StyledButton,
)
from core.converter import (
    convert_vegas_to_resolve,
    convert_resolve_to_vegas,
    ConversionResult,
)


class TimelineBridgeApp:
    """Main application window."""

    WINDOW_TITLE = "Vegas ↔ Resolve Timeline Bridge"
    WINDOW_MIN_WIDTH = 720
    WINDOW_MIN_HEIGHT = 640

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.configure(bg=COLORS["bg_primary"])
        self.root.minsize(self.WINDOW_MIN_WIDTH, self.WINDOW_MIN_HEIGHT)
        self.root.geometry("780x700")

        # Try to set the window icon (if available)
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        # State variables
        self.mode_var = tk.StringVar(value="vegas_to_resolve")
        self.input_path_var = tk.StringVar()
        self.is_converting = False

        # Build the UI
        self._build_header()
        self._build_mode_selector()
        self._build_file_input()
        self._build_remap_section()
        self._build_convert_button()
        self._build_log_panel()
        self._build_status_bar()

    # ======================================================================
    # UI Construction
    # ======================================================================

    def _build_header(self):
        """Top banner with app name and version."""
        header_frame = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # App icon + title
        title = tk.Label(
            header_frame,
            text="🎬  Vegas ↔ Resolve Timeline Bridge",
            font=("Segoe UI Bold", 16),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_secondary"],
        )
        title.pack(side="left", padx=16, pady=12)

        # Version badge
        version = tk.Label(
            header_frame,
            text="v1.0.0",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            padx=8,
            pady=2,
        )
        version.pack(side="right", padx=16, pady=20)

    def _build_mode_selector(self):
        """Radio buttons for conversion direction."""
        frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        frame.pack(fill="x", padx=16, pady=(16, 8))

        SectionHeader(frame, text="Conversion Mode").pack(anchor="w")

        radio_frame = tk.Frame(frame, bg=COLORS["bg_primary"])
        radio_frame.pack(fill="x", pady=(6, 0))

        # Style the radio buttons
        style = ttk.Style()
        style.configure(
            "Dark.TRadiobutton",
            background=COLORS["bg_primary"],
            foreground=COLORS["text_primary"],
            font=("Segoe UI", 11),
            indicatordiameter=16,
        )
        style.map("Dark.TRadiobutton",
                   background=[("active", COLORS["bg_primary"])],
                   foreground=[("active", COLORS["text_accent"])])

        vegas_radio = ttk.Radiobutton(
            radio_frame,
            text="🎬  Vegas Pro → DaVinci Resolve   (cut in Vegas, grade in Resolve)",
            variable=self.mode_var,
            value="vegas_to_resolve",
            style="Dark.TRadiobutton",
        )
        vegas_radio.pack(anchor="w", pady=2)

        resolve_radio = ttk.Radiobutton(
            radio_frame,
            text="🎨  DaVinci Resolve → Vegas Pro   (bring graded timeline back)",
            variable=self.mode_var,
            value="resolve_to_vegas",
            style="Dark.TRadiobutton",
        )
        resolve_radio.pack(anchor="w", pady=2)

    def _build_file_input(self):
        """File browser for input XML."""
        frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        frame.pack(fill="x", padx=16, pady=(12, 8))

        SectionHeader(frame, text="Input XML File").pack(anchor="w")

        input_row = tk.Frame(frame, bg=COLORS["bg_primary"])
        input_row.pack(fill="x", pady=(6, 0))

        self.file_entry = StyledEntry(
            input_row,
            placeholder="Click Browse to select your XML file...",
            textvariable=self.input_path_var,
        )
        self.file_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        browse_btn = StyledButton(
            input_row,
            text="📂 Browse",
            command=self._browse_file,
            accent=False,
        )
        browse_btn.pack(side="right")

    def _build_remap_section(self):
        """Path prefix remapping fields."""
        frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        frame.pack(fill="x", padx=16, pady=(12, 8))

        SectionHeader(
            frame,
            text="Path Remapping (Optional — fix drive letters / folder changes)",
        ).pack(anchor="w")

        # Source prefix
        src_row = tk.Frame(frame, bg=COLORS["bg_primary"])
        src_row.pack(fill="x", pady=(6, 2))

        tk.Label(
            src_row,
            text="Find:",
            font=("Segoe UI", 10),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_primary"],
            width=6,
            anchor="e",
        ).pack(side="left")

        self.remap_src_entry = StyledEntry(
            src_row,
            placeholder=r"e.g.  C:\OldProjects\  or  D:\Footage\"
        )
        self.remap_src_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(6, 0))

        # Destination prefix
        dst_row = tk.Frame(frame, bg=COLORS["bg_primary"])
        dst_row.pack(fill="x", pady=2)

        tk.Label(
            dst_row,
            text="Replace:",
            font=("Segoe UI", 10),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_primary"],
            width=6,
            anchor="e",
        ).pack(side="left")

        self.remap_dst_entry = StyledEntry(
            dst_row,
            placeholder=r"e.g.  E:\Media\  or  D:\NewFootage\"
        )
        self.remap_dst_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(6, 0))

    def _build_convert_button(self):
        """The big Convert button."""
        frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        frame.pack(fill="x", padx=16, pady=(16, 8))

        self.convert_btn = StyledButton(
            frame,
            text="⚡  Convert Timeline",
            command=self._start_conversion,
        )
        self.convert_btn.pack(fill="x", ipady=4)

    def _build_log_panel(self):
        """Scrollable log output."""
        self.log_panel = LogPanel(self.root)
        self.log_panel.pack(fill="both", expand=True, padx=16, pady=(0, 4))

    def _build_status_bar(self):
        """Bottom status bar."""
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill="x", side="bottom")

    # ======================================================================
    # Actions
    # ======================================================================

    def _browse_file(self):
        """Open a file dialog to select the input XML."""
        mode = self.mode_var.get()
        title = (
            "Select VEGAS Pro exported XML"
            if mode == "vegas_to_resolve"
            else "Select DaVinci Resolve exported XML"
        )

        filepath = filedialog.askopenfilename(
            title=title,
            filetypes=[
                ("XML Files", "*.xml"),
                ("All Files", "*.*"),
            ],
        )

        if filepath:
            self.input_path_var.set(filepath)
            # Update the entry display (clear placeholder)
            self.file_entry.configure(fg=COLORS["text_primary"])
            self.log_panel.log("info", f"Selected: {filepath}")

    def _start_conversion(self):
        """Validate inputs and run the conversion in a background thread."""
        if self.is_converting:
            return

        # Validate input file
        input_path = self.input_path_var.get().strip()
        if not input_path or input_path == self.file_entry.placeholder:
            self.status_bar.set_error("No file selected")
            self.log_panel.log("error", "Please select an XML file first.")
            return

        if not os.path.isfile(input_path):
            self.status_bar.set_error("File not found")
            self.log_panel.log("error", f"File does not exist: {input_path}")
            return

        # Get remapping values
        remap_src = self.remap_src_entry.get_value()
        remap_dst = self.remap_dst_entry.get_value()

        # Disable button and start
        self.is_converting = True
        self.convert_btn.configure(state="disabled", text="⏳  Converting...")
        self.status_bar.set_processing()
        self.log_panel.clear()
        self.log_panel.log("info", "Starting conversion...")

        # Run in background thread to keep GUI responsive
        thread = threading.Thread(
            target=self._run_conversion,
            args=(input_path, remap_src, remap_dst),
            daemon=True,
        )
        thread.start()

    def _run_conversion(self, input_path: str, remap_src: str, remap_dst: str):
        """Execute the conversion (runs in background thread)."""

        # Thread-safe log function that posts to Tkinter's event loop
        def log_fn(level: str, message: str):
            self.root.after(0, self.log_panel.log, level, message)

        mode = self.mode_var.get()

        try:
            if mode == "vegas_to_resolve":
                result = convert_vegas_to_resolve(
                    input_path,
                    remap_src=remap_src,
                    remap_dst=remap_dst,
                    log_fn=log_fn,
                )
            else:
                result = convert_resolve_to_vegas(
                    input_path,
                    remap_src=remap_src,
                    remap_dst=remap_dst,
                    log_fn=log_fn,
                )

            # Update UI on main thread
            self.root.after(0, self._on_conversion_complete, result)

        except Exception as e:
            self.root.after(0, self._on_conversion_error, str(e))

    def _on_conversion_complete(self, result: ConversionResult):
        """Handle conversion completion (main thread)."""
        self.is_converting = False
        self.convert_btn.configure(state="normal", text="⚡  Convert Timeline")

        if result.success:
            if result.mode == "vegas_to_resolve":
                summary = (
                    f"✓ {result.paths_converted} paths fixed, "
                    f"{result.effects_removed + result.filters_removed} effects stripped, "
                    f"{result.links_preserved} links preserved"
                )
            else:
                summary = (
                    f"✓ {result.paths_converted} paths converted, "
                    f"{result.links_preserved} links preserved"
                )

            self.status_bar.set_success(summary)
            self.log_panel.log("success", "─" * 50)
            self.log_panel.log("success", f"Output saved: {result.output_path}")
            self.log_panel.log("success", summary)
        else:
            error_msg = "; ".join(result.errors) if result.errors else "Unknown error"
            self.status_bar.set_error(error_msg)
            self.log_panel.log("error", f"Conversion failed: {error_msg}")

    def _on_conversion_error(self, error: str):
        """Handle unexpected errors (main thread)."""
        self.is_converting = False
        self.convert_btn.configure(state="normal", text="⚡  Convert Timeline")
        self.status_bar.set_error(f"Unexpected error: {error}")
        self.log_panel.log("error", f"Unexpected error: {error}")

    # ======================================================================
    # Launch
    # ======================================================================

    def run(self):
        """Start the Tkinter main loop."""
        # Center the window on screen
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

        self.root.mainloop()
