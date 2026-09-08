"""
widgets.py — Reusable Tkinter widget components for the Timeline Bridge GUI.

Provides:
  - LogPanel: scrollable, color-coded log output
  - StatusBar: bottom status bar with summary text
  - SectionHeader: styled section label
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional


# ---------------------------------------------------------------------------
# Color palette — dark theme inspired by Resolve/Vegas aesthetics
# ---------------------------------------------------------------------------

COLORS = {
    "bg_primary":     "#1a1a2e",   # Deep navy background
    "bg_secondary":   "#16213e",   # Slightly lighter panel
    "bg_input":       "#0f3460",   # Input field background
    "bg_button":      "#e94560",   # Accent red (action button)
    "bg_button_hover":"#ff6b6b",   # Button hover
    "bg_success":     "#00b894",   # Green success
    "bg_card":        "#1e2a4a",   # Card/frame background
    "text_primary":   "#eaeaea",   # Main text
    "text_secondary": "#a0a0b0",   # Subdued text
    "text_accent":    "#e94560",   # Accent text
    "text_success":   "#00b894",   # Success text
    "text_warning":   "#fdcb6e",   # Warning text
    "text_error":     "#ff6b6b",   # Error text
    "text_info":      "#74b9ff",   # Info text
    "border":         "#2d3a5f",   # Subtle border
    "highlight":      "#e94560",   # Selection/focus highlight
}

LOG_COLORS = {
    "info":    COLORS["text_info"],
    "success": COLORS["text_success"],
    "warning": COLORS["text_warning"],
    "error":   COLORS["text_error"],
}


# ---------------------------------------------------------------------------
# LogPanel — scrollable log output with color-coded messages
# ---------------------------------------------------------------------------

class LogPanel(tk.Frame):
    """Scrollable log output with color-coded messages.

    Usage:
        panel = LogPanel(parent)
        panel.log("info", "Processing file...")
        panel.log("success", "✓ Done!")
        panel.log("error", "Failed to write output")
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_secondary"], **kwargs)

        # Header
        header = tk.Label(
            self,
            text="📋 Conversion Log",
            font=("Segoe UI Semibold", 11),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_secondary"],
            anchor="w",
        )
        header.pack(fill="x", padx=10, pady=(8, 4))

        # Text area
        self.text = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=("Cascadia Code", 10),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            selectbackground=COLORS["highlight"],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=8,
            height=12,
            state="disabled",
        )
        self.text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Configure color tags
        for level, color in LOG_COLORS.items():
            self.text.tag_configure(level, foreground=color)

        self.text.tag_configure("timestamp", foreground=COLORS["text_secondary"])

    def log(self, level: str, message: str) -> None:
        """Append a log message with color coding.

        Args:
            level:   One of "info", "success", "warning", "error".
            message: The log message text.
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        self.text.configure(state="normal")

        # Insert timestamp
        self.text.insert("end", f"[{timestamp}] ", "timestamp")

        # Insert level badge
        badge = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✗"}.get(level, "•")
        self.text.insert("end", f"{badge} {message}\n", level)

        # Auto-scroll to bottom
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self) -> None:
        """Clear all log messages."""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")


# ---------------------------------------------------------------------------
# StatusBar — bottom summary bar
# ---------------------------------------------------------------------------

class StatusBar(tk.Frame):
    """Bottom status bar showing conversion summary."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], height=36, **kwargs)
        self.pack_propagate(False)

        self.label = tk.Label(
            self,
            text="Ready — select an XML file to begin",
            font=("Segoe UI", 10),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            anchor="w",
            padx=12,
        )
        self.label.pack(fill="both", expand=True)

    def set_status(self, text: str, level: str = "info") -> None:
        """Update status text and color.

        Args:
            text:  Status message.
            level: One of "info", "success", "warning", "error".
        """
        color = LOG_COLORS.get(level, COLORS["text_secondary"])
        self.label.configure(text=text, fg=color)

    def set_ready(self) -> None:
        self.set_status("Ready — select an XML file to begin", "info")

    def set_processing(self) -> None:
        self.set_status("⏳ Processing...", "warning")

    def set_success(self, summary: str) -> None:
        self.set_status(f"✓ {summary}", "success")

    def set_error(self, message: str) -> None:
        self.set_status(f"✗ {message}", "error")


# ---------------------------------------------------------------------------
# SectionHeader — styled label for form sections
# ---------------------------------------------------------------------------

class SectionHeader(tk.Label):
    """Styled section header label."""

    def __init__(self, parent, text: str, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=("Segoe UI Semibold", 11),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_primary"],
            anchor="w",
            **kwargs,
        )


# ---------------------------------------------------------------------------
# StyledEntry — input field with dark theme
# ---------------------------------------------------------------------------

class StyledEntry(tk.Entry):
    """Dark-themed input field."""

    def __init__(self, parent, placeholder: str = "", **kwargs):
        super().__init__(
            parent,
            font=("Segoe UI", 10),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            selectbackground=COLORS["highlight"],
            relief="flat",
            borderwidth=0,
            **kwargs,
        )
        self.placeholder = placeholder
        self._show_placeholder()

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(fg=COLORS["text_secondary"])

    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, "end")
            self.configure(fg=COLORS["text_primary"])

    def _on_focus_out(self, event):
        if not self.get():
            self._show_placeholder()

    def get_value(self) -> str:
        """Get the actual value, ignoring placeholder text."""
        val = self.get()
        return "" if val == self.placeholder else val


# ---------------------------------------------------------------------------
# StyledButton — accent-colored button
# ---------------------------------------------------------------------------

class StyledButton(tk.Button):
    """Dark-themed button with hover effects."""

    def __init__(self, parent, text: str, command=None, accent: bool = True, **kwargs):
        bg = COLORS["bg_button"] if accent else COLORS["bg_card"]
        hover = COLORS["bg_button_hover"] if accent else COLORS["border"]

        super().__init__(
            parent,
            text=text,
            command=command,
            font=("Segoe UI Semibold", 11),
            fg=COLORS["text_primary"],
            bg=bg,
            activebackground=hover,
            activeforeground=COLORS["text_primary"],
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=20,
            pady=8,
            **kwargs,
        )

        self._bg = bg
        self._hover = hover
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))
