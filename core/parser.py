"""
parser.py — XMEML (FCP7 XML) parsing engine.

Loads VEGAS Pro 2026 or DaVinci Resolve Studio 21 exported XML files,
validates the XMEML structure, and provides iteration helpers for
pathurls, file elements, effects/filters, timecodes, and links.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional


# ---------------------------------------------------------------------------
# Data classes for structured results
# ---------------------------------------------------------------------------

@dataclass
class XMEMLInfo:
    """Metadata extracted from the root <xmeml> element."""
    version: str = ""
    has_project: bool = False
    has_sequence: bool = False
    sequence_name: str = ""
    sequence_duration: Optional[int] = None
    sequence_timebase: Optional[float] = None


@dataclass
class ParseStats:
    """Statistics collected during parsing."""
    total_pathurls: int = 0
    total_file_elements: int = 0
    total_effects: int = 0
    total_filters: int = 0
    total_links: int = 0
    total_clipitems: int = 0
    total_tracks: int = 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class XMEMLParser:
    """Parser for FCP7 XMEML files exported by VEGAS Pro or DaVinci Resolve.

    Usage:
        parser = XMEMLParser("timeline.xml")
        for pathurl_elem in parser.find_all_pathurls():
            print(pathurl_elem.text)
    """

    def __init__(self, xml_path: str):
        self.xml_path = Path(xml_path)
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self._load()

    # -- Loading & validation -----------------------------------------------

    def _load(self) -> None:
        """Load and validate the XML file."""
        if not self.xml_path.exists():
            raise FileNotFoundError(f"XML file not found: {self.xml_path}")

        if not self.xml_path.suffix.lower() == ".xml":
            raise ValueError(f"Expected .xml file, got: {self.xml_path.suffix}")

        self.tree = ET.parse(str(self.xml_path))
        self.root = self.tree.getroot()

        if self.root.tag != "xmeml":
            raise ValueError(
                f"Not a valid XMEML file. Root tag is <{self.root.tag}>, "
                f"expected <xmeml>."
            )

    def get_info(self) -> XMEMLInfo:
        """Extract high-level info from the XMEML structure."""
        info = XMEMLInfo()
        info.version = self.root.get("version", "")

        project = self.root.find(".//project")
        info.has_project = project is not None

        seq = self.root.find(".//sequence")
        info.has_sequence = seq is not None

        if seq is not None:
            name_elem = seq.find("name")
            info.sequence_name = name_elem.text if name_elem is not None and name_elem.text else ""

            dur_elem = seq.find("duration")
            if dur_elem is not None and dur_elem.text:
                try:
                    info.sequence_duration = int(dur_elem.text)
                except ValueError:
                    pass

            tb_elem = seq.find("rate/timebase")
            if tb_elem is not None and tb_elem.text:
                try:
                    info.sequence_timebase = float(tb_elem.text)
                except ValueError:
                    pass

        return info

    def get_stats(self) -> ParseStats:
        """Count all relevant elements in the XML tree."""
        stats = ParseStats()
        stats.total_pathurls = len(list(self.find_all_pathurls()))
        stats.total_file_elements = len(list(self.find_all_file_elements()))
        stats.total_effects = len(list(self.find_all_effects()))
        stats.total_filters = len(list(self.find_all_filters()))
        stats.total_links = len(list(self.find_all_links()))
        stats.total_clipitems = len(list(self.root.iter("clipitem")))
        stats.total_tracks = len(list(self.root.iter("track")))
        return stats

    # -- Element iterators --------------------------------------------------

    def find_all_pathurls(self) -> Iterator[ET.Element]:
        """Yield every <pathurl> element in the tree."""
        yield from self.root.iter("pathurl")

    def find_all_file_elements(self) -> Iterator[ET.Element]:
        """Yield every <file> element in the tree."""
        yield from self.root.iter("file")

    def find_all_effects(self) -> Iterator[ET.Element]:
        """Yield every <effect> element in the tree."""
        yield from self.root.iter("effect")

    def find_all_filters(self) -> Iterator[ET.Element]:
        """Yield every <filter> element in the tree."""
        yield from self.root.iter("filter")

    def find_all_links(self) -> Iterator[ET.Element]:
        """Yield every <link> element (A/V sync references)."""
        yield from self.root.iter("link")

    def find_all_clipitems(self) -> Iterator[ET.Element]:
        """Yield every <clipitem> element."""
        yield from self.root.iter("clipitem")

    def find_all_tracks(self) -> Iterator[ET.Element]:
        """Yield every <track> element."""
        yield from self.root.iter("track")

    def find_all_sequences(self) -> Iterator[ET.Element]:
        """Yield every <sequence> element."""
        yield from self.root.iter("sequence")

    def find_sequence_rate(self) -> Optional[ET.Element]:
        """Find the primary sequence's <rate> element."""
        seq = self.root.find(".//sequence")
        if seq is not None:
            return seq.find("rate")
        return None

    # -- Tree access --------------------------------------------------------

    def get_tree(self) -> ET.ElementTree:
        """Return the parsed ElementTree for direct manipulation."""
        return self.tree

    def get_root(self) -> ET.Element:
        """Return the root <xmeml> element."""
        return self.root

    def write(self, output_path: str) -> None:
        """Write the (possibly modified) XML tree to a new file.

        Uses xml_declaration and UTF-8 encoding to match XMEML conventions.
        """
        self.tree.write(
            output_path,
            encoding="UTF-8",
            xml_declaration=True,
        )
