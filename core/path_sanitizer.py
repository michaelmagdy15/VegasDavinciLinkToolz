"""
path_sanitizer.py — Path conversion between Windows native paths and RFC 3986 file URIs.

VEGAS Pro 2026 exports absolute Windows paths (backslashes, no URI scheme).
DaVinci Resolve Studio 21 expects file://localhost/ URIs with URL-encoded specials.
This module handles both directions plus batch prefix remapping.
"""

import re
from urllib.parse import quote, unquote, urlparse, urlunparse


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FILE_URI_PREFIX = "file://localhost/"
FILE_URI_PREFIX_ALT = "file:///"  # Some apps use triple-slash without "localhost"


# ---------------------------------------------------------------------------
# Windows path → Resolve file URI
# ---------------------------------------------------------------------------

def normalize_separators(path: str) -> str:
    """Replace all backslashes with forward slashes.

    >>> normalize_separators(r"D:\\Footage\\My Clip.mp4")
    'D:/Footage/My Clip.mp4'
    """
    return path.replace("\\", "/")


def url_encode_path(path: str) -> str:
    """URL-encode a path string per RFC 3986.

    Encodes spaces, unicode, and special chars but preserves
    forward slashes (/) and colons (:) that are structural.

    >>> url_encode_path("D:/Footage/My Clip (v2).mp4")
    'D:/Footage/My%20Clip%20%28v2%29.mp4'
    """
    # safe="/:@" keeps drive letters (C:), slashes, and @ intact
    return quote(path, safe="/:@")


def url_decode_path(encoded_path: str) -> str:
    """Decode a URL-encoded path back to a plain string.

    >>> url_decode_path("D:/Footage/My%20Clip%20%28v2%29.mp4")
    'D:/Footage/My Clip (v2).mp4'
    """
    return unquote(encoded_path)


def windows_path_to_file_uri(path: str) -> str:
    """Convert an absolute Windows path to a Resolve-compatible file URI.

    Pipeline:
      1. Normalize backslashes to forward slashes.
      2. Strip any existing file:// prefix to avoid double-prepending.
      3. URL-encode special characters.
      4. Prepend file://localhost/.

    >>> windows_path_to_file_uri(r"D:\\Footage\\My Clip.mp4")
    'file://localhost/D:/Footage/My%20Clip.mp4'
    """
    # Step 1 — normalize separators
    clean = normalize_separators(path)

    # Step 2 — strip existing URI prefix if present (idempotency)
    for prefix in (FILE_URI_PREFIX, FILE_URI_PREFIX_ALT):
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break

    # Step 3 — URL-encode
    encoded = url_encode_path(clean)

    # Step 4 — prepend the Resolve-expected prefix
    return FILE_URI_PREFIX + encoded


# ---------------------------------------------------------------------------
# Resolve file URI → Windows path
# ---------------------------------------------------------------------------

def file_uri_to_windows_path(uri: str) -> str:
    """Convert a file://localhost/ URI back to a native Windows path.

    Pipeline:
      1. Strip the file://localhost/ (or file:///) prefix.
      2. URL-decode percent-encoded characters.
      3. Convert forward slashes to backslashes.

    >>> file_uri_to_windows_path("file://localhost/D:/Footage/My%20Clip.mp4")
    'D:\\\\Footage\\\\My Clip.mp4'
    """
    clean = uri

    # Strip known prefixes
    for prefix in (FILE_URI_PREFIX, FILE_URI_PREFIX_ALT):
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break

    # URL-decode
    decoded = url_decode_path(clean)

    # Forward slashes → backslashes for Windows
    return decoded.replace("/", "\\")


# ---------------------------------------------------------------------------
# Batch prefix remapping
# ---------------------------------------------------------------------------

def remap_path_prefix(path: str, src_prefix: str, dst_prefix: str) -> str:
    """Replace a source path prefix with a destination prefix.

    Both prefixes are normalized to forward slashes before matching
    so the user can enter either style.

    >>> remap_path_prefix("C:/OldProjects/Shot01/clip.mp4",
    ...                   "C:/OldProjects/", "E:/Media/")
    'E:/Media/Shot01/clip.mp4'
    """
    norm_path = normalize_separators(path)
    norm_src = normalize_separators(src_prefix)
    norm_dst = normalize_separators(dst_prefix)

    # Ensure prefixes end with "/" for clean matching
    if norm_src and not norm_src.endswith("/"):
        norm_src += "/"
    if norm_dst and not norm_dst.endswith("/"):
        norm_dst += "/"

    if norm_path.startswith(norm_src):
        return norm_dst + norm_path[len(norm_src):]

    # No match — return unchanged
    return path


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

def is_file_uri(path: str) -> bool:
    """Check whether a string is already a file:// URI."""
    return path.startswith("file://")


def is_windows_absolute_path(path: str) -> bool:
    """Check whether a string looks like an absolute Windows path (e.g. D:\\...)."""
    # Matches drive letter followed by colon and separator
    return bool(re.match(r'^[A-Za-z]:[/\\]', path))


def needs_conversion_to_uri(path: str) -> bool:
    """Return True if the path is a Windows path that should become a file URI."""
    return is_windows_absolute_path(path) and not is_file_uri(path)


def needs_conversion_to_windows(path: str) -> bool:
    """Return True if the path is a file URI that should become a Windows path."""
    return is_file_uri(path)


# ---------------------------------------------------------------------------
# Universal Environment & Installation Discovery (Zero Hardcoded User Paths)
# ---------------------------------------------------------------------------

def get_bridge_dir():
    """Return Path to ~/.timeline_bridge in the current user profile."""
    from pathlib import Path
    p = Path.home() / ".timeline_bridge"
    p.mkdir(parents=True, exist_ok=True)
    return p


def find_all_vegas_installations():
    """Discover all installed VEGAS Pro versions across BorisFX, MAGIX, and Sony directories.

    Returns:
        List of dicts with 'name', 'version', 'executable', 'script_menu_dir'.
    """
    import os
    from pathlib import Path

    installations = []
    seen_dirs = set()

    prog_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    app_data = os.environ.get("APPDATA", "")

    # Common installation roots
    candidates = [
        (Path(prog_files) / "BorisFX" / "Vegas Pro 2026", "BorisFX Vegas Pro 2026", "2026.0"),
        (Path(prog_files) / "VEGAS" / "VEGAS Pro 23.0", "VEGAS Pro 23.0", "23.0"),
        (Path(prog_files) / "VEGAS" / "Vegas Pro 22", "VEGAS Pro 22.0", "22.0"),
        (Path(prog_files) / "VEGAS" / "VEGAS Pro 21.0", "VEGAS Pro 21.0", "21.0"),
        (Path(prog_files) / "VEGAS" / "VEGAS Pro 20.0", "VEGAS Pro 20.0", "20.0"),
        (Path(prog_files) / "Sony" / "Vegas Pro 13.0", "Sony Vegas Pro 13.0", "13.0"),
    ]

    for cdir, cname, cver in candidates:
        if cdir.exists() and str(cdir).lower() not in seen_dirs:
            seen_dirs.add(str(cdir).lower())
            exe_path = None
            for exe in cdir.glob("*.exe"):
                if "vegas" in exe.name.lower():
                    exe_path = str(exe)
                    break

            app_script_dir = None
            if app_data:
                app_cand = Path(app_data) / "VEGAS Pro" / cver / "Script Menu"
                if app_cand.parent.exists():
                    app_script_dir = str(app_cand)

            installations.append({
                "name": cname,
                "version": cver,
                "install_dir": str(cdir),
                "executable": exe_path,
                "script_menu_dir": app_script_dir or str(cdir / "Script Menu"),
            })

    return installations


def find_resolve_installation():
    """Discover DaVinci Resolve installation and scripting modules.

    Returns:
        Dict with 'app_dir', 'fusionscript_dll', 'script_modules_dir', 'available'.
    """
    import os
    from pathlib import Path

    prog_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    prog_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")

    resolve_dir = Path(prog_files) / "Blackmagic Design" / "DaVinci Resolve"
    fusion_dll = resolve_dir / "fusionscript.dll"
    modules_dir = Path(prog_data) / "Blackmagic Design" / "DaVinci Resolve" / "Support" / "Developer" / "Scripting" / "Modules"

    available = fusion_dll.exists()

    return {
        "app_dir": str(resolve_dir) if resolve_dir.exists() else None,
        "fusionscript_dll": str(fusion_dll) if fusion_dll.exists() else None,
        "script_modules_dir": str(modules_dir) if modules_dir.exists() else None,
        "available": available,
    }

