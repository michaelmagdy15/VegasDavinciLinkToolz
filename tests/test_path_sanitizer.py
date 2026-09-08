"""
test_path_sanitizer.py — Tests for Windows ↔ file:// URI conversion.
"""

import unittest
from core.path_sanitizer import (
    normalize_separators,
    url_encode_path,
    url_decode_path,
    windows_path_to_file_uri,
    file_uri_to_windows_path,
    remap_path_prefix,
    is_file_uri,
    is_windows_absolute_path,
    needs_conversion_to_uri,
    needs_conversion_to_windows,
)


class TestNormalizeSeparators(unittest.TestCase):

    def test_backslashes_to_forward(self):
        self.assertEqual(
            normalize_separators(r"D:\Footage\Clip1.mp4"),
            "D:/Footage/Clip1.mp4",
        )

    def test_mixed_separators(self):
        self.assertEqual(
            normalize_separators(r"D:\Footage/SubDir\Clip.mp4"),
            "D:/Footage/SubDir/Clip.mp4",
        )

    def test_already_forward_slashes(self):
        self.assertEqual(
            normalize_separators("D:/Footage/Clip1.mp4"),
            "D:/Footage/Clip1.mp4",
        )


class TestURLEncoding(unittest.TestCase):

    def test_spaces_encoded(self):
        self.assertEqual(
            url_encode_path("D:/My Footage/Clip 1.mp4"),
            "D:/My%20Footage/Clip%201.mp4",
        )

    def test_parentheses_encoded(self):
        result = url_encode_path("D:/Footage/Take (3).mp4")
        self.assertIn("%28", result)
        self.assertIn("%29", result)

    def test_slashes_preserved(self):
        result = url_encode_path("D:/Footage/Sub/Clip.mp4")
        self.assertNotIn("%2F", result)

    def test_drive_colon_preserved(self):
        result = url_encode_path("D:/Footage/Clip.mp4")
        self.assertTrue(result.startswith("D:"))

    def test_round_trip(self):
        original = "D:/My Project/Shoot (Day 1)/Clip #5.mp4"
        encoded = url_encode_path(original)
        decoded = url_decode_path(encoded)
        self.assertEqual(decoded, original)


class TestWindowsPathToFileURI(unittest.TestCase):

    def test_simple_path(self):
        self.assertEqual(
            windows_path_to_file_uri(r"D:\Footage\Clip1.mp4"),
            "file://localhost/D:/Footage/Clip1.mp4",
        )

    def test_path_with_spaces(self):
        result = windows_path_to_file_uri(r"D:\My Footage\Clip 1.mp4")
        self.assertEqual(
            result,
            "file://localhost/D:/My%20Footage/Clip%201.mp4",
        )

    def test_path_with_special_chars(self):
        result = windows_path_to_file_uri(r"D:\Footage\Take (3).mp4")
        self.assertTrue(result.startswith("file://localhost/"))
        self.assertIn("%28", result)
        self.assertIn("%29", result)

    def test_idempotent_already_uri(self):
        """Converting a path that already has a file:// prefix should not double-up."""
        uri = "file://localhost/D:/Footage/Clip.mp4"
        result = windows_path_to_file_uri(uri)
        self.assertEqual(result, uri)

    def test_forward_slash_input(self):
        result = windows_path_to_file_uri("D:/Footage/Clip.mp4")
        self.assertEqual(result, "file://localhost/D:/Footage/Clip.mp4")


class TestFileURIToWindowsPath(unittest.TestCase):

    def test_simple_uri(self):
        self.assertEqual(
            file_uri_to_windows_path("file://localhost/D:/Footage/Clip1.mp4"),
            r"D:\Footage\Clip1.mp4",
        )

    def test_uri_with_encoded_spaces(self):
        self.assertEqual(
            file_uri_to_windows_path("file://localhost/D:/My%20Footage/Clip%201.mp4"),
            r"D:\My Footage\Clip 1.mp4",
        )

    def test_uri_with_encoded_parens(self):
        result = file_uri_to_windows_path(
            "file://localhost/D:/Footage/Take%20%283%29.mp4"
        )
        self.assertEqual(result, r"D:\Footage\Take (3).mp4")

    def test_triple_slash_variant(self):
        self.assertEqual(
            file_uri_to_windows_path("file:///D:/Footage/Clip.mp4"),
            r"D:\Footage\Clip.mp4",
        )

    def test_round_trip_windows_to_uri_and_back(self):
        original = r"D:\Projects\Wedding 2026\Footage\Ceremony Wide.mp4"
        uri = windows_path_to_file_uri(original)
        restored = file_uri_to_windows_path(uri)
        self.assertEqual(restored, original)


class TestRemapPathPrefix(unittest.TestCase):

    def test_simple_remap(self):
        self.assertEqual(
            remap_path_prefix(
                "C:/OldProjects/Shot01/clip.mp4",
                "C:/OldProjects/",
                "E:/Media/",
            ),
            "E:/Media/Shot01/clip.mp4",
        )

    def test_remap_no_trailing_slash(self):
        """Prefixes without trailing slashes should still work."""
        self.assertEqual(
            remap_path_prefix(
                "C:/OldProjects/Shot01/clip.mp4",
                "C:/OldProjects",
                "E:/Media",
            ),
            "E:/Media/Shot01/clip.mp4",
        )

    def test_no_match_returns_original(self):
        original = "D:/Footage/clip.mp4"
        self.assertEqual(
            remap_path_prefix(original, "C:/OldProjects/", "E:/Media/"),
            original,
        )

    def test_backslash_input(self):
        result = remap_path_prefix(
            r"C:\OldProjects\Shot01\clip.mp4",
            r"C:\OldProjects",
            r"E:\Media",
        )
        self.assertEqual(result, "E:/Media/Shot01/clip.mp4")


class TestDetectionHelpers(unittest.TestCase):

    def test_is_file_uri(self):
        self.assertTrue(is_file_uri("file://localhost/D:/foo.mp4"))
        self.assertTrue(is_file_uri("file:///D:/foo.mp4"))
        self.assertFalse(is_file_uri(r"D:\foo.mp4"))

    def test_is_windows_absolute_path(self):
        self.assertTrue(is_windows_absolute_path(r"D:\Footage\Clip.mp4"))
        self.assertTrue(is_windows_absolute_path("C:/Footage/Clip.mp4"))
        self.assertFalse(is_windows_absolute_path("file://localhost/D:/foo.mp4"))
        self.assertFalse(is_windows_absolute_path("relative/path.mp4"))

    def test_needs_conversion_to_uri(self):
        self.assertTrue(needs_conversion_to_uri(r"D:\Footage\Clip.mp4"))
        self.assertFalse(needs_conversion_to_uri("file://localhost/D:/Clip.mp4"))

    def test_needs_conversion_to_windows(self):
        self.assertTrue(needs_conversion_to_windows("file://localhost/D:/Clip.mp4"))
        self.assertFalse(needs_conversion_to_windows(r"D:\Footage\Clip.mp4"))


if __name__ == "__main__":
    unittest.main()
