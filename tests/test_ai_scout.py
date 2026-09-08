"""
test_ai_scout.py — Tests for the automated Motion & Visual Action Scout.
"""

import os
import json
import pytest
from core.ai_scout import export_selects_manifest, analyze_clip_action


def test_export_selects_manifest(tmp_path):
    selects = [
        {
            "name": "TestClip_01",
            "media_path": "D:/Footage/TestClip_01.mov",
            "source_in_ms": 3200.0,
            "length_ms": 2500.0,
            "score": 0.92,
            "label": "[ACTION] Big Air Takeoff",
        },
        {
            "name": "TestClip_02",
            "media_path": "D:/Footage/TestClip_02.mov",
            "source_in_ms": 11500.0,
            "length_ms": 2200.0,
            "score": 0.85,
            "label": "[ACTION] Fast Spray Carve",
        },
    ]

    out_file = tmp_path / "test_selects.json"
    result = export_selects_manifest(selects, manifest_name="Test Scout", output_path=str(out_file))

    assert os.path.exists(result)
    with open(result, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["manifest_name"] == "Test Scout"
    assert data["clip_count"] == 2
    assert len(data["clips"]) == 2
    assert data["clips"][0]["source_in_ms"] == 3200.0


def test_analyze_clip_nonexistent():
    # Nonexistent file should return empty gracefully
    res = analyze_clip_action("C:/nonexistent_fake_video.mov")
    assert res == []
