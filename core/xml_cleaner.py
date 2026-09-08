"""
xml_cleaner.py — Strip VEGAS-proprietary metadata and normalize timecodes.

VEGAS Pro 2026 injects effect/filter nodes that DaVinci Resolve Studio 21
cannot parse. This module removes them while preserving Resolve-safe effects,
<link> tags (A/V sync), and ensuring consistent <rate> across the tree.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional, Set


# ---------------------------------------------------------------------------
# Whitelist: effects that Resolve understands from FCP7 XML
# ---------------------------------------------------------------------------

# These effectid values are part of the FCP7 standard and are parsed
# correctly by Resolve.  Everything else is VEGAS-proprietary and will
# either crash the import or produce a silent wrong result.
RESOLVE_SAFE_EFFECT_IDS: Set[str] = {
    # Motion & transform
    "basic motion",
    "motion",
    # Opacity / compositing
    "opacity",
    # Audio
    "audio levels",
    "audiolevels",
    # Standard transitions
    "cross dissolve",
    "crossdissolve",
    "dip to color",
    "diptocolor",
    "dip to colour",      # Resolve UK spelling variant
    "fade in",
    "fadein",
    "fade out",
    "fadeout",
    "additive dissolve",
    "additivedissolve",
    # Text generators Resolve can read
    "text",
    # Time remap
    "time remap",
    "timeremap",
    "speed",
}

# VEGAS-specific effect names that are ALWAYS stripped regardless of context
VEGAS_KNOWN_JUNK: Set[str] = {
    "track motion",
    "trackmotion",
    "vegas track motion",
    "vegas video fx",
    "vegas audio fx",
    "sony track motion",
    "sony video fx",
    "sony audio fx",
    "magix track motion",
    "magix video fx",
    "magix audio fx",
    "vegasimagesequence",
    "vegas pan/crop",
    "pan/crop",
    "pancrop",
}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

@dataclass
class CleaningStats:
    """Statistics from a cleaning pass."""
    effects_removed: int = 0
    effects_kept: int = 0
    filters_removed: int = 0
    filters_kept: int = 0
    timecodes_fixed: int = 0
    links_preserved: int = 0
    empty_tracks_removed: int = 0
    sequence_files_populated: int = 0


# ---------------------------------------------------------------------------
# Effect / filter cleaning
# ---------------------------------------------------------------------------

def _get_effect_id(element: ET.Element) -> str:
    """Extract the <effectid> or <name> text from an effect/filter, lowercased."""
    # Try <effectid> first (standard FCP7)
    eid = element.find("effectid")
    if eid is not None and eid.text:
        return eid.text.strip().lower()

    # Try <effect>/<name> inside a <filter>
    effect_child = element.find("effect")
    if effect_child is not None:
        eid2 = effect_child.find("effectid")
        if eid2 is not None and eid2.text:
            return eid2.text.strip().lower()
        name2 = effect_child.find("name")
        if name2 is not None and name2.text:
            return name2.text.strip().lower()

    # Fall back to <name>
    name = element.find("name")
    if name is not None and name.text:
        return name.text.strip().lower()

    return ""


def is_resolve_safe_effect(effect_id: str) -> bool:
    """Return True if the effect is known to be Resolve-compatible."""
    return effect_id in RESOLVE_SAFE_EFFECT_IDS


def is_vegas_junk_effect(effect_id: str) -> bool:
    """Return True if the effect is known VEGAS proprietary junk."""
    if effect_id in VEGAS_KNOWN_JUNK:
        return True
    # Catch anything with "vegas", "sony", "magix" in the name
    for vendor in ("vegas", "sony", "magix"):
        if vendor in effect_id:
            return True
    return False


def strip_unsafe_effects(root: ET.Element) -> tuple:
    """Remove <effect> nodes that are not in the Resolve-safe whitelist.

    Effects nested inside <clipitem> or <track> are checked.
    Returns (removed_count, kept_count).
    """
    removed = 0
    kept = 0

    # We need to iterate parent→child so we can remove children from parents
    for parent in root.iter():
        effects_to_remove: List[ET.Element] = []

        for child in parent:
            if child.tag == "effect":
                eid = _get_effect_id(child)
                if is_resolve_safe_effect(eid):
                    kept += 1
                else:
                    effects_to_remove.append(child)

        for effect in effects_to_remove:
            parent.remove(effect)
            removed += 1

    return removed, kept


def strip_unsafe_filters(root: ET.Element) -> tuple:
    """Remove <filter> nodes whose inner <effect> is not Resolve-safe.

    Filters wrap effects in XMEML:
        <filter>
            <effect>
                <name>Vegas Track Motion</name>
                <effectid>trackmotion</effectid>
            </effect>
        </filter>

    Returns (removed_count, kept_count).
    """
    removed = 0
    kept = 0

    for parent in root.iter():
        filters_to_remove: List[ET.Element] = []

        for child in parent:
            if child.tag == "filter":
                eid = _get_effect_id(child)
                if is_resolve_safe_effect(eid):
                    kept += 1
                else:
                    filters_to_remove.append(child)

        for filt in filters_to_remove:
            parent.remove(filt)
            removed += 1

    return removed, kept


# ---------------------------------------------------------------------------
# Timecode / rate normalization
# ---------------------------------------------------------------------------

def normalize_timecodes(root: ET.Element) -> int:
    """Ensure consistent <rate><timebase> across the whole tree.

    Strategy:
      1. Read the <rate> from the first <sequence> found (the master rate).
      2. For every <clipitem> and <track> that has a <rate>, verify it matches.
      3. If a <clipitem> is missing <rate> entirely, inject a copy of the
         sequence rate so Resolve doesn't guess wrong.

    Returns the number of timecodes fixed/injected.
    """
    fixed = 0

    # Find the master sequence rate
    seq = root.find(".//sequence")
    if seq is None:
        return 0

    seq_rate = seq.find("rate")
    if seq_rate is None:
        return 0

    master_timebase = seq_rate.find("timebase")
    master_ntsc = seq_rate.find("ntsc")

    if master_timebase is None or not master_timebase.text:
        return 0

    master_tb_val = master_timebase.text.strip()
    master_ntsc_val = master_ntsc.text.strip() if master_ntsc is not None and master_ntsc.text else "FALSE"

    # Fix rates in clipitems
    for clipitem in root.iter("clipitem"):
        clip_rate = clipitem.find("rate")

        if clip_rate is None:
            # Inject rate element
            new_rate = ET.SubElement(clipitem, "rate")
            tb = ET.SubElement(new_rate, "timebase")
            tb.text = master_tb_val
            ntsc = ET.SubElement(new_rate, "ntsc")
            ntsc.text = master_ntsc_val
            fixed += 1
        else:
            # Verify and fix existing rate
            clip_tb = clip_rate.find("timebase")
            if clip_tb is not None and clip_tb.text and clip_tb.text.strip() != master_tb_val:
                clip_tb.text = master_tb_val
                fixed += 1

            clip_ntsc = clip_rate.find("ntsc")
            if clip_ntsc is None:
                ntsc = ET.SubElement(clip_rate, "ntsc")
                ntsc.text = master_ntsc_val
                fixed += 1
            elif clip_ntsc.text and clip_ntsc.text.strip() != master_ntsc_val:
                clip_ntsc.text = master_ntsc_val
                fixed += 1

    return fixed


# ---------------------------------------------------------------------------
# Link preservation count
# ---------------------------------------------------------------------------

def count_links(root: ET.Element) -> int:
    """Count all <link> elements (A/V synchronization references).

    These are NEVER modified — this is just for reporting.
    """
    return len(list(root.iter("link")))


# ---------------------------------------------------------------------------
# Empty track cleanup
# ---------------------------------------------------------------------------

def remove_empty_tracks(root: ET.Element) -> int:
    """Remove <track> elements that contain zero <clipitem> children.

    VEGAS sometimes exports empty placeholder tracks that clutter Resolve's
    timeline.  Returns the number of tracks removed.
    """
    removed = 0

    for parent in root.iter():
        tracks_to_remove = []
        for child in parent:
            if child.tag == "track":
                clipitems = child.findall("clipitem")
                if len(clipitems) == 0:
                    tracks_to_remove.append(child)

        for track in tracks_to_remove:
            parent.remove(track)
            removed += 1

    return removed


def populate_sequence_files(root: ET.Element) -> int:
    """Populate empty <file id="..."/> stubs in <sequence> with full metadata.

    VEGAS Pro exports define the full file details (including <name> and <pathurl>)
    inside master clips in <project><children><clip>, but only write empty
    <file id="..."/> reference stubs inside the timeline <sequence>.
    DaVinci Resolve strictly expects <pathurl> to be inside each sequence clip's
    <file> element, otherwise it prompts 'clips were not yet found'.
    """
    import copy

    # Collect master file definitions from everywhere in the document
    file_defs = {}
    for f in root.findall(".//file"):
        fid = f.get("id")
        if fid and len(f) > 0 and f.find("pathurl") is not None:
            if fid not in file_defs:
                file_defs[fid] = f

    populated = 0
    seq = root.find(".//sequence")
    if seq is None:
        return 0

    for f in seq.findall(".//file"):
        if len(f) == 0:
            fid = f.get("id")
            master = file_defs.get(fid)
            if master is not None:
                for child in master:
                    f.append(copy.deepcopy(child))
                populated += 1

    return populated


# ---------------------------------------------------------------------------
# Full cleaning pass
# ---------------------------------------------------------------------------

def clean_xml_for_resolve(root: ET.Element, remove_empty: bool = True) -> CleaningStats:
    """Run the full cleaning pipeline on an XMEML tree.

    1. Populate empty sequence file stubs with full pathurls and metadata
    2. Strip unsafe effects
    3. Strip unsafe filters
    4. Normalize timecodes
    5. Count preserved links
    6. Optionally remove empty tracks

    Returns a CleaningStats with counts for every action.
    """
    stats = CleaningStats()

    stats.sequence_files_populated = populate_sequence_files(root)
    stats.effects_removed, stats.effects_kept = strip_unsafe_effects(root)
    stats.filters_removed, stats.filters_kept = strip_unsafe_filters(root)
    stats.timecodes_fixed = normalize_timecodes(root)
    stats.links_preserved = count_links(root)

    if remove_empty:
        stats.empty_tracks_removed = remove_empty_tracks(root)

    return stats
