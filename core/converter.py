"""
converter.py — Orchestrates the full VEGAS ↔ Resolve conversion pipeline.

Ties together the parser, path_sanitizer, and xml_cleaner into a single
high-level API that the GUI calls.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from core.parser import XMEMLParser, ParseStats, XMEMLInfo
from core.path_sanitizer import (
    windows_path_to_file_uri,
    file_uri_to_windows_path,
    remap_path_prefix,
    normalize_separators,
    needs_conversion_to_uri,
    needs_conversion_to_windows,
    is_file_uri,
)
from core.xml_cleaner import CleaningStats, clean_xml_for_resolve


# ---------------------------------------------------------------------------
# Result data class
# ---------------------------------------------------------------------------

@dataclass
class ConversionResult:
    """Full result from a conversion run."""
    success: bool = False
    input_path: str = ""
    output_path: str = ""
    mode: str = ""  # "vegas_to_resolve" or "resolve_to_vegas"

    # XML info
    xmeml_version: str = ""
    sequence_name: str = ""

    # Path stats
    total_pathurls_found: int = 0
    paths_converted: int = 0
    paths_remapped: int = 0
    paths_already_correct: int = 0

    # Cleaning stats (Vegas→Resolve only)
    effects_removed: int = 0
    effects_kept: int = 0
    filters_removed: int = 0
    filters_kept: int = 0
    timecodes_fixed: int = 0
    links_preserved: int = 0
    empty_tracks_removed: int = 0

    # Parse stats
    total_clipitems: int = 0
    total_tracks: int = 0

    # Errors
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Log callback type
# ---------------------------------------------------------------------------

# The GUI passes a log function: log_fn(level, message)
# level is one of: "info", "warning", "error", "success"
LogCallback = Callable[[str, str], None]


def _noop_log(level: str, message: str) -> None:
    """Default no-op logger."""
    pass


# ---------------------------------------------------------------------------
# Output path generation
# ---------------------------------------------------------------------------

def _generate_output_path(input_path: str, mode: str) -> str:
    """Generate the output filename by appending a suffix before the extension.

    vegas_to_resolve: "timeline.xml" → "timeline_for_resolve.xml"
    resolve_to_vegas: "timeline.xml" → "timeline_for_vegas.xml"
    """
    p = Path(input_path)
    suffix = "_for_resolve" if mode == "vegas_to_resolve" else "_for_vegas"
    return str(p.parent / f"{p.stem}{suffix}{p.suffix}")


# ---------------------------------------------------------------------------
# Vegas → Resolve conversion
# ---------------------------------------------------------------------------

def convert_vegas_to_resolve(
    xml_path: str,
    output_path: Optional[str] = None,
    remap_src: str = "",
    remap_dst: str = "",
    log_fn: LogCallback = _noop_log,
) -> ConversionResult:
    """Convert a VEGAS Pro exported XMEML to a DaVinci Resolve compatible one.

    Pipeline:
      1. Parse the XMEML file.
      2. Convert all <pathurl> Windows paths to file://localhost/ URIs.
      3. Apply prefix remapping if provided.
      4. Strip VEGAS-proprietary effects and filters.
      5. Normalize timecodes across the tree.
      6. Write the cleaned XML to the output path.

    Args:
        xml_path:    Path to the VEGAS-exported XML file.
        output_path: Where to write the cleaned XML. Auto-generated if None.
        remap_src:   Source prefix to replace (e.g., "C:\\OldProjects\\").
        remap_dst:   Destination prefix (e.g., "E:\\Media\\").
        log_fn:      Callback for logging progress.

    Returns:
        ConversionResult with full stats.
    """
    result = ConversionResult(mode="vegas_to_resolve", input_path=xml_path)

    if output_path is None:
        output_path = _generate_output_path(xml_path, "vegas_to_resolve")
    result.output_path = output_path

    # --- Step 1: Parse ---
    log_fn("info", f"Loading XML: {xml_path}")
    try:
        parser = XMEMLParser(xml_path)
    except (FileNotFoundError, ValueError) as e:
        result.errors.append(str(e))
        log_fn("error", str(e))
        return result

    info = parser.get_info()
    result.xmeml_version = info.version
    result.sequence_name = info.sequence_name
    log_fn("info", f"XMEML v{info.version} — Sequence: '{info.sequence_name}'")

    root = parser.get_root()

    # --- Step 2 & 3: Path conversion ---
    log_fn("info", "Converting paths to Resolve file:// URIs...")

    for pathurl in root.iter("pathurl"):
        if pathurl.text is None:
            continue

        result.total_pathurls_found += 1
        original = pathurl.text.strip()

        # Apply prefix remapping first (before URI conversion)
        current = original
        if remap_src and remap_dst:
            remapped = remap_path_prefix(
                normalize_separators(current), remap_src, remap_dst
            )
            if remapped != normalize_separators(current):
                current = remapped
                result.paths_remapped += 1
                log_fn("info", f"  Remapped: {original} → {current}")

        # Convert to file URI if needed
        if needs_conversion_to_uri(current):
            converted = windows_path_to_file_uri(current)
            pathurl.text = converted
            result.paths_converted += 1
            log_fn("info", f"  Converted: {current} → {converted}")
        elif is_file_uri(current):
            # Already a valid URI — but might need re-encoding
            # Normalize it through our pipeline for consistency
            pathurl.text = current
            result.paths_already_correct += 1
        else:
            # Relative path or unknown format — convert anyway
            converted = windows_path_to_file_uri(current)
            pathurl.text = converted
            result.paths_converted += 1
            log_fn("warning", f"  Non-standard path converted: {current} → {converted}")

    log_fn("success",
           f"Paths: {result.paths_converted} converted, "
           f"{result.paths_remapped} remapped, "
           f"{result.paths_already_correct} already correct")

    # --- Step 4 & 5: XML cleaning ---
    log_fn("info", "Cleaning VEGAS-specific metadata...")
    cleaning_stats = clean_xml_for_resolve(root)

    result.effects_removed = cleaning_stats.effects_removed
    result.effects_kept = cleaning_stats.effects_kept
    result.filters_removed = cleaning_stats.filters_removed
    result.filters_kept = cleaning_stats.filters_kept
    result.timecodes_fixed = cleaning_stats.timecodes_fixed
    result.links_preserved = cleaning_stats.links_preserved
    result.empty_tracks_removed = cleaning_stats.empty_tracks_removed

    log_fn("success",
           f"Effects: {result.effects_removed} removed, {result.effects_kept} kept")
    log_fn("success",
           f"Filters: {result.filters_removed} removed, {result.filters_kept} kept")

    if result.timecodes_fixed > 0:
        log_fn("info", f"Timecodes: {result.timecodes_fixed} fixed/injected")

    log_fn("info", f"Links preserved: {result.links_preserved}")

    if result.empty_tracks_removed > 0:
        log_fn("info", f"Empty tracks removed: {result.empty_tracks_removed}")

    # --- Step 6: Collect final stats ---
    final_stats = parser.get_stats()
    result.total_clipitems = final_stats.total_clipitems
    result.total_tracks = final_stats.total_tracks

    # --- Step 7: Write output ---
    log_fn("info", f"Writing output: {output_path}")
    try:
        parser.write(output_path)
        result.success = True
        log_fn("success", f"✓ Conversion complete → {output_path}")
    except Exception as e:
        result.errors.append(f"Write failed: {e}")
        log_fn("error", f"Write failed: {e}")

    return result


# ---------------------------------------------------------------------------
# Resolve → Vegas conversion
# ---------------------------------------------------------------------------

def convert_resolve_to_vegas(
    xml_path: str,
    output_path: Optional[str] = None,
    remap_src: str = "",
    remap_dst: str = "",
    log_fn: LogCallback = _noop_log,
) -> ConversionResult:
    """Convert a DaVinci Resolve exported XMEML back to VEGAS-readable format.

    Pipeline:
      1. Parse the XMEML file.
      2. Convert all file://localhost/ URIs to native Windows paths.
      3. Apply prefix remapping if provided.
      4. Write the converted XML to the output path.

    Note: No effect stripping in this direction — Resolve exports clean XML.
    """
    result = ConversionResult(mode="resolve_to_vegas", input_path=xml_path)

    if output_path is None:
        output_path = _generate_output_path(xml_path, "resolve_to_vegas")
    result.output_path = output_path

    # --- Step 1: Parse ---
    log_fn("info", f"Loading XML: {xml_path}")
    try:
        parser = XMEMLParser(xml_path)
    except (FileNotFoundError, ValueError) as e:
        result.errors.append(str(e))
        log_fn("error", str(e))
        return result

    info = parser.get_info()
    result.xmeml_version = info.version
    result.sequence_name = info.sequence_name
    log_fn("info", f"XMEML v{info.version} — Sequence: '{info.sequence_name}'")

    root = parser.get_root()

    # --- Step 2 & 3: Path conversion ---
    log_fn("info", "Converting file:// URIs to Windows paths...")

    for pathurl in root.iter("pathurl"):
        if pathurl.text is None:
            continue

        result.total_pathurls_found += 1
        original = pathurl.text.strip()

        if needs_conversion_to_windows(original):
            win_path = file_uri_to_windows_path(original)

            # Apply prefix remapping
            if remap_src and remap_dst:
                remapped = remap_path_prefix(
                    normalize_separators(win_path),
                    normalize_separators(remap_src),
                    normalize_separators(remap_dst),
                )
                if remapped != normalize_separators(win_path):
                    win_path = remapped.replace("/", "\\")
                    result.paths_remapped += 1
                    log_fn("info", f"  Remapped: {original} → {win_path}")

            pathurl.text = win_path
            result.paths_converted += 1
            log_fn("info", f"  Converted: {original} → {win_path}")
        else:
            result.paths_already_correct += 1

    log_fn("success",
           f"Paths: {result.paths_converted} converted, "
           f"{result.paths_remapped} remapped, "
           f"{result.paths_already_correct} already correct")

    # --- Step 4: Collect stats ---
    final_stats = parser.get_stats()
    result.total_clipitems = final_stats.total_clipitems
    result.total_tracks = final_stats.total_tracks
    result.links_preserved = len(list(root.iter("link")))

    # --- Step 5: Write output ---
    log_fn("info", f"Writing output: {output_path}")
    try:
        parser.write(output_path)
        result.success = True
        log_fn("success", f"✓ Conversion complete → {output_path}")
    except Exception as e:
        result.errors.append(f"Write failed: {e}")
        log_fn("error", f"Write failed: {e}")

    return result
