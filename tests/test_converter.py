"""
test_converter.py — Integration tests for the full Vegas ↔ Resolve pipeline.

Tests the converter module with the sample fixture XMLs.
"""

import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from core.converter import (
    convert_vegas_to_resolve,
    convert_resolve_to_vegas,
    ConversionResult,
)


# Fixture paths
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
VEGAS_SAMPLE = os.path.join(FIXTURES_DIR, "vegas_sample.xml")
RESOLVE_SAMPLE = os.path.join(FIXTURES_DIR, "resolve_sample.xml")


class TestVegasToResolve(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.output = os.path.join(self.tmpdir, "output.xml")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_conversion_succeeds(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        self.assertTrue(result.success, f"Errors: {result.errors}")
        self.assertTrue(os.path.exists(self.output))

    def test_paths_converted_to_uris(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        tree = ET.parse(self.output)
        for pathurl in tree.iter("pathurl"):
            if pathurl.text:
                self.assertTrue(
                    pathurl.text.startswith("file://localhost/"),
                    f"Path not converted: {pathurl.text}",
                )

    def test_spaces_encoded_in_paths(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        tree = ET.parse(self.output)
        for pathurl in tree.iter("pathurl"):
            if pathurl.text and " " in pathurl.text:
                # The only spaces should be inside the "file://localhost/" prefix,
                # NOT in the actual path portion
                path_part = pathurl.text.replace("file://localhost/", "")
                self.assertNotIn(
                    " ", path_part,
                    f"Unencoded space in path: {pathurl.text}",
                )

    def test_vegas_effects_stripped(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        self.assertGreater(result.effects_removed + result.filters_removed, 0)

        tree = ET.parse(self.output)
        for effect in tree.iter("effect"):
            eid = effect.find("effectid")
            if eid is not None and eid.text:
                self.assertNotIn("trackmotion", eid.text.lower())
                self.assertNotIn("pancrop", eid.text.lower())
                self.assertNotIn("vegas", eid.text.lower())
                self.assertNotIn("sony", eid.text.lower())
                self.assertNotIn("magix", eid.text.lower())

    def test_safe_effects_preserved(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        self.assertGreater(result.effects_kept + result.filters_kept, 0)

    def test_links_preserved(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        self.assertGreater(result.links_preserved, 0)

        tree = ET.parse(self.output)
        links = list(tree.iter("link"))
        self.assertGreater(len(links), 0)

    def test_empty_tracks_removed(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        self.assertGreater(result.empty_tracks_removed, 0)

    def test_stats_populated(self):
        result = convert_vegas_to_resolve(VEGAS_SAMPLE, self.output)
        self.assertGreater(result.total_pathurls_found, 0)
        self.assertGreater(result.paths_converted, 0)
        self.assertEqual(result.mode, "vegas_to_resolve")

    def test_path_remapping(self):
        result = convert_vegas_to_resolve(
            VEGAS_SAMPLE,
            self.output,
            remap_src="D:/Projects/Wedding 2026/Footage",
            remap_dst="E:/Media/Wedding",
        )
        self.assertTrue(result.success)
        tree = ET.parse(self.output)
        found_remapped = False
        for pathurl in tree.iter("pathurl"):
            if pathurl.text and "Media/Wedding" in pathurl.text:
                found_remapped = True
        self.assertTrue(found_remapped, "No paths were remapped")

    def test_log_callback_called(self):
        messages = []

        def log_fn(level, msg):
            messages.append((level, msg))

        convert_vegas_to_resolve(VEGAS_SAMPLE, self.output, log_fn=log_fn)
        self.assertGreater(len(messages), 0)
        levels = {m[0] for m in messages}
        self.assertIn("info", levels)
        self.assertIn("success", levels)


class TestResolveToVegas(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.output = os.path.join(self.tmpdir, "output.xml")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_conversion_succeeds(self):
        result = convert_resolve_to_vegas(RESOLVE_SAMPLE, self.output)
        self.assertTrue(result.success, f"Errors: {result.errors}")
        self.assertTrue(os.path.exists(self.output))

    def test_uris_converted_to_windows_paths(self):
        result = convert_resolve_to_vegas(RESOLVE_SAMPLE, self.output)
        tree = ET.parse(self.output)
        for pathurl in tree.iter("pathurl"):
            if pathurl.text:
                self.assertFalse(
                    pathurl.text.startswith("file://"),
                    f"URI not converted: {pathurl.text}",
                )
                self.assertIn("\\", pathurl.text, f"Not a Windows path: {pathurl.text}")

    def test_encoded_chars_decoded(self):
        result = convert_resolve_to_vegas(RESOLVE_SAMPLE, self.output)
        tree = ET.parse(self.output)
        for pathurl in tree.iter("pathurl"):
            if pathurl.text:
                self.assertNotIn("%20", pathurl.text)
                self.assertNotIn("%28", pathurl.text)

    def test_links_preserved(self):
        result = convert_resolve_to_vegas(RESOLVE_SAMPLE, self.output)
        self.assertGreater(result.links_preserved, 0)

    def test_stats_populated(self):
        result = convert_resolve_to_vegas(RESOLVE_SAMPLE, self.output)
        self.assertGreater(result.total_pathurls_found, 0)
        self.assertGreater(result.paths_converted, 0)
        self.assertEqual(result.mode, "resolve_to_vegas")


class TestRoundTrip(unittest.TestCase):
    """Test that converting Vegas→Resolve→Vegas preserves clip structure."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_round_trip_preserves_clips(self):
        # Step 1: Vegas → Resolve
        resolve_xml = os.path.join(self.tmpdir, "step1_resolve.xml")
        r1 = convert_vegas_to_resolve(VEGAS_SAMPLE, resolve_xml)
        self.assertTrue(r1.success)

        # Step 2: Resolve → Vegas
        vegas_xml = os.path.join(self.tmpdir, "step2_vegas.xml")
        r2 = convert_resolve_to_vegas(resolve_xml, vegas_xml)
        self.assertTrue(r2.success)

        # Verify structure is intact
        tree = ET.parse(vegas_xml)
        clipitems = list(tree.iter("clipitem"))
        self.assertGreater(len(clipitems), 0, "No clipitems after round-trip")

        links = list(tree.iter("link"))
        self.assertGreater(len(links), 0, "No links after round-trip")

    def test_round_trip_paths_are_windows(self):
        resolve_xml = os.path.join(self.tmpdir, "step1.xml")
        convert_vegas_to_resolve(VEGAS_SAMPLE, resolve_xml)

        vegas_xml = os.path.join(self.tmpdir, "step2.xml")
        convert_resolve_to_vegas(resolve_xml, vegas_xml)

        tree = ET.parse(vegas_xml)
        for pathurl in tree.iter("pathurl"):
            if pathurl.text and pathurl.text.strip():
                self.assertFalse(
                    pathurl.text.startswith("file://"),
                    f"Round-trip failed — still a URI: {pathurl.text}",
                )


if __name__ == "__main__":
    unittest.main()
