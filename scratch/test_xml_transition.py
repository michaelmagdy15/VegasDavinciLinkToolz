import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()

xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <sequence id="test_trans_seq">
    <name>Test Transition Sync</name>
    <rate>
      <timebase>24</timebase>
      <ntsc>FALSE</ntsc>
    </rate>
    <media>
      <video>
        <format>
          <samplecharacteristics>
            <rate>
              <timebase>24</timebase>
              <ntsc>FALSE</ntsc>
            </rate>
            <width>1080</width>
            <height>1920</height>
          </samplecharacteristics>
        </format>
        <track>
          <clipitem id="clip-1">
            <name>filmburn_6.mov</name>
            <duration>100</duration>
            <rate><timebase>24</timebase><ntsc>FALSE</ntsc></rate>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <file id="f-1">
              <name>filmburn_6.mov</name>
              <pathurl>file://localhost/E:/Video%20Editing%20Resource/Filmburns/filmburn_6.mov</pathurl>
              <rate><timebase>24</timebase><ntsc>FALSE</ntsc></rate>
              <duration>100</duration>
            </file>
          </clipitem>
          <transitionitem>
            <start>80</start>
            <end>100</end>
            <alignment>end</alignment>
            <effect>
              <name>Cross Dissolve</name>
              <effectid>Cross Dissolve</effectid>
              <effecttype>transition</effecttype>
              <mediatype>video</mediatype>
            </effect>
          </transitionitem>
        </track>
      </video>
    </media>
  </sequence>
</xmeml>"""

test_xml_path = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\test_trans.xml"
with open(test_xml_path, "w", encoding="utf-8") as f:
    f.write(xml_content)

print(f"Written test XML: {test_xml_path}")
imported_tl = mp.ImportTimelineFromFile(test_xml_path, {"timelineName": "Test Transition Sync"})
print("Imported timeline result:", imported_tl)
if imported_tl:
    print("Successfully imported timeline with transition!")
    # Check items on V1
    vitems = imported_tl.GetItemListInTrack("video", 1) or []
    print(f"Items on V1: {len(vitems)}")
    # Clean up test timeline
    # proj.DeleteTimeline(imported_tl)
