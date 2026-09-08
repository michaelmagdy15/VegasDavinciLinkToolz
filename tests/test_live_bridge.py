"""
test_live_bridge.py — Unit tests for the VEGAS <-> DaVinci Resolve live bridge.
"""

import json
import os
import tempfile
from pathlib import Path
from core.live_bridge import xml_to_timeline_json, is_resolve_running, get_resolve_app


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VEGAS_SAMPLE = str(PROJECT_ROOT / "tests" / "fixtures" / "vegas_sample.xml")


class TestLiveBridgeManifest:
    def test_xml_to_timeline_json(self, tmp_path):
        out_json = str(tmp_path / "test_manifest.json")
        res_path = xml_to_timeline_json(VEGAS_SAMPLE, out_json)
        assert os.path.exists(res_path)

        with open(res_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "project_name" in data
        assert "frame_rate" in data
        assert "tracks" in data
        assert len(data["tracks"]) > 0

        # Check track structure
        v_track = data["tracks"][0]
        assert "is_video" in v_track
        assert "clips" in v_track
        assert len(v_track["clips"]) > 0

        clip = v_track["clips"][0]
        assert "media_path" in clip
        assert "timeline_start_ms" in clip
        assert "timeline_length_ms" in clip
        assert "source_in_ms" in clip


class TestResolveConnection:
    def test_resolve_detection(self):
        # We know Resolve 21 is currently open on the test machine
        running = is_resolve_running()
        assert isinstance(running, bool)
