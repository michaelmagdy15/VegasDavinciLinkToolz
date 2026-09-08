#!/usr/bin/env bash
# Vegas <-> Resolve Timeline Bridge Launcher
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

if [ -n "$1" ]; then
    "$PYTHON_BIN" main.py "$1"
else
    "$PYTHON_BIN" main.py
fi
