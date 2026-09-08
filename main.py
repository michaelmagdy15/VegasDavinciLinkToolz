"""
Vegas ↔ DaVinci Resolve Timeline Bridge
========================================
Entry point — launches the GUI.

Usage:
    python main.py
"""

import sys
import os

# Ensure the project root is on the Python path so imports work
# regardless of where the script is launched from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import TimelineBridgeApp


def main():
    app = TimelineBridgeApp()
    app.run()


if __name__ == "__main__":
    main()
