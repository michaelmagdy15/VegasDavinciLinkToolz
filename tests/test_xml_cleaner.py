"""
test_xml_cleaner.py — Tests for VEGAS effect stripping, timecode normalization,
                      link preservation, and empty track removal.
"""

import unittest
import xml.etree.ElementTree as ET

from core.xml_cleaner import (
    is_resolve_safe_effect,
    is_vegas_junk_effect,
    strip_unsafe_effects,
    strip_unsafe_filters,
    normalize_timecodes,
    count_links,
    remove_empty_tracks,
    clean_xml_for_resolve,
)


class TestEffectClassification(unittest.TestCase):

    def test_safe_effects(self):
        for eid in ("opacity", "basic motion", "audio levels", "cross dissolve"):
            self.assertTrue(is_resolve_safe_effect(eid), f"{eid} should be safe")

    def test_unsafe_effects(self):
        for eid in ("trackmotion", "pancrop", "magix video fx", "sony audio fx"):
            self.assertFalse(is_resolve_safe_effect(eid), f"{eid} should not be safe")

    def test_vegas_junk_detection(self):
        self.assertTrue(is_vegas_junk_effect("trackmotion"))
        self.assertTrue(is_vegas_junk_effect("vegas video fx"))
        self.assertTrue(is_vegas_junk_effect("sony audio fx"))
        self.assertTrue(is_vegas_junk_effect("magix track motion"))

    def test_non_junk_detection(self):
        self.assertFalse(is_vegas_junk_effect("opacity"))
        self.assertFalse(is_vegas_junk_effect("cross dissolve"))


class TestStripUnsafeEffects(unittest.TestCase):

    def test_removes_vegas_effects(self):
        xml = ET.fromstring("""
        <clipitem>
            <effect>
                <name>Vegas Pan/Crop</name>
                <effectid>pancrop</effectid>
            </effect>
            <effect>
                <name>Opacity</name>
                <effectid>opacity</effectid>
            </effect>
        </clipitem>
        """)
        removed, kept = strip_unsafe_effects(xml)
        self.assertEqual(removed, 1)
        self.assertEqual(kept, 1)
        # Only opacity should remain
        effects = xml.findall("effect")
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].find("effectid").text, "opacity")

    def test_keeps_all_safe_effects(self):
        xml = ET.fromstring("""
        <clipitem>
            <effect>
                <name>Opacity</name>
                <effectid>opacity</effectid>
            </effect>
            <effect>
                <name>Basic Motion</name>
                <effectid>basic motion</effectid>
            </effect>
        </clipitem>
        """)
        removed, kept = strip_unsafe_effects(xml)
        self.assertEqual(removed, 0)
        self.assertEqual(kept, 2)


class TestStripUnsafeFilters(unittest.TestCase):

    def test_removes_vegas_filters(self):
        xml = ET.fromstring("""
        <clipitem>
            <filter>
                <effect>
                    <name>Vegas Track Motion</name>
                    <effectid>trackmotion</effectid>
                </effect>
            </filter>
            <filter>
                <effect>
                    <name>Audio Levels</name>
                    <effectid>audiolevels</effectid>
                </effect>
            </filter>
        </clipitem>
        """)
        removed, kept = strip_unsafe_filters(xml)
        self.assertEqual(removed, 1)
        self.assertEqual(kept, 1)

    def test_keeps_standard_transitions(self):
        xml = ET.fromstring("""
        <clipitem>
            <filter>
                <effect>
                    <name>Cross Dissolve</name>
                    <effectid>cross dissolve</effectid>
                </effect>
            </filter>
        </clipitem>
        """)
        removed, kept = strip_unsafe_filters(xml)
        self.assertEqual(removed, 0)
        self.assertEqual(kept, 1)


class TestTimecodeNormalization(unittest.TestCase):

    def test_injects_missing_rate(self):
        xml = ET.fromstring("""
        <xmeml version="5">
            <sequence>
                <rate>
                    <timebase>24</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
                <media>
                    <video>
                        <track>
                            <clipitem>
                                <name>No Rate Clip</name>
                            </clipitem>
                        </track>
                    </video>
                </media>
            </sequence>
        </xmeml>
        """)
        fixed = normalize_timecodes(xml)
        self.assertGreater(fixed, 0)
        # Clip should now have a rate
        clip = xml.find(".//clipitem")
        rate = clip.find("rate")
        self.assertIsNotNone(rate)
        self.assertEqual(rate.find("timebase").text, "24")

    def test_fixes_mismatched_rate(self):
        xml = ET.fromstring("""
        <xmeml version="5">
            <sequence>
                <rate>
                    <timebase>24</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
                <media>
                    <video>
                        <track>
                            <clipitem>
                                <name>Wrong Rate</name>
                                <rate>
                                    <timebase>30</timebase>
                                    <ntsc>FALSE</ntsc>
                                </rate>
                            </clipitem>
                        </track>
                    </video>
                </media>
            </sequence>
        </xmeml>
        """)
        fixed = normalize_timecodes(xml)
        self.assertGreater(fixed, 0)
        clip_tb = xml.find(".//clipitem/rate/timebase")
        self.assertEqual(clip_tb.text, "24")


class TestCountLinks(unittest.TestCase):

    def test_counts_links(self):
        xml = ET.fromstring("""
        <xmeml>
            <clipitem>
                <link><linkclipref>a</linkclipref></link>
            </clipitem>
            <clipitem>
                <link><linkclipref>b</linkclipref></link>
                <link><linkclipref>c</linkclipref></link>
            </clipitem>
        </xmeml>
        """)
        self.assertEqual(count_links(xml), 3)


class TestRemoveEmptyTracks(unittest.TestCase):

    def test_removes_empty_tracks(self):
        xml = ET.fromstring("""
        <video>
            <track>
                <clipitem><name>Clip 1</name></clipitem>
            </track>
            <track>
            </track>
        </video>
        """)
        removed = remove_empty_tracks(xml)
        self.assertEqual(removed, 1)
        tracks = xml.findall("track")
        self.assertEqual(len(tracks), 1)

    def test_keeps_populated_tracks(self):
        xml = ET.fromstring("""
        <video>
            <track>
                <clipitem><name>Clip 1</name></clipitem>
            </track>
            <track>
                <clipitem><name>Clip 2</name></clipitem>
            </track>
        </video>
        """)
        removed = remove_empty_tracks(xml)
        self.assertEqual(removed, 0)


class TestCleanXMLForResolve(unittest.TestCase):

    def test_full_cleaning_pipeline(self):
        xml = ET.fromstring("""
        <xmeml version="5">
            <sequence>
                <rate>
                    <timebase>24</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
                <media>
                    <video>
                        <track>
                            <clipitem>
                                <name>Clip</name>
                                <filter>
                                    <effect>
                                        <name>Vegas Track Motion</name>
                                        <effectid>trackmotion</effectid>
                                    </effect>
                                </filter>
                                <filter>
                                    <effect>
                                        <name>Opacity</name>
                                        <effectid>opacity</effectid>
                                    </effect>
                                </filter>
                                <link><linkclipref>audio-1</linkclipref></link>
                            </clipitem>
                        </track>
                        <track>
                        </track>
                    </video>
                </media>
            </sequence>
        </xmeml>
        """)
        stats = clean_xml_for_resolve(xml)
        self.assertEqual(stats.filters_removed, 1)
        self.assertEqual(stats.filters_kept, 1)
        self.assertGreater(stats.links_preserved, 0)
        self.assertEqual(stats.empty_tracks_removed, 1)


if __name__ == "__main__":
    unittest.main()
