"""
test_cli.py — Tests for main.py command-line interface.
"""

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VEGAS_SAMPLE = str(PROJECT_ROOT / "tests" / "fixtures" / "vegas_sample.xml")
RESOLVE_SAMPLE = str(PROJECT_ROOT / "tests" / "fixtures" / "resolve_sample.xml")


def run_main(*args):
    cmd = [sys.executable, "main.py", *args]
    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result


class TestCLIHelp:
    def test_help_flag(self):
        res = run_main("--help")
        assert res.returncode == 0
        assert "Vegas <-> DaVinci Resolve Timeline Bridge" in res.stdout
        assert "--cli" in res.stdout
        assert "--mode" in res.stdout

    def test_short_help_flag(self):
        res = run_main("-h")
        assert res.returncode == 0


class TestCLIExecution:
    def test_cli_missing_input_file(self):
        res = run_main("--cli")
        assert res.returncode != 0
        assert "must be specified" in (res.stderr + res.stdout)

    def test_cli_nonexistent_file(self):
        res = run_main("--cli", "nonexistent_file_12345.xml")
        assert res.returncode != 0
        assert "File not found" in (res.stderr + res.stdout)

    def test_cli_vegas_to_resolve_conversion(self, tmp_path):
        out_file = str(tmp_path / "out_resolve.xml")
        res = run_main(
            VEGAS_SAMPLE,
            "--cli",
            "-m", "vegas_to_resolve",
            "-o", out_file,
        )
        assert res.returncode == 0
        assert os.path.exists(out_file)
        assert "[OK] Successfully converted" in res.stdout

    def test_cli_resolve_to_vegas_conversion(self, tmp_path):
        out_file = str(tmp_path / "out_vegas.xml")
        res = run_main(
            RESOLVE_SAMPLE,
            "--cli",
            "-m", "resolve_to_vegas",
            "-o", out_file,
        )
        assert res.returncode == 0
        assert os.path.exists(out_file)
        assert "[OK] Successfully converted" in res.stdout

    def test_cli_with_path_remapping(self, tmp_path):
        out_file = str(tmp_path / "out_remapped.xml")
        res = run_main(
            VEGAS_SAMPLE,
            "--cli",
            "--remap-src", "D:/Projects",
            "--remap-dst", "Z:/StudioShare",
            "-o", out_file,
        )
        assert res.returncode == 0
        assert os.path.exists(out_file)
        with open(out_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Z%3A/StudioShare" in content or "Z:/StudioShare" in content
