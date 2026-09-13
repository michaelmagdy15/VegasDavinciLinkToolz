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
  <sequence id="test_audio_vol_seq">
    <name>Test Audio Vol Sync</name>
    <rate><timebase>24</timebase><ntsc>FALSE</ntsc></rate>
    <media>
      <video>
        <format>
          <samplecharacteristics>
            <rate><timebase>24</timebase><ntsc>FALSE</ntsc></rate>
            <width>1080</width>
            <height>1920</height>
          </samplecharacteristics>
        </format>
      </video>
      <audio>
        <track>
          <clipitem id="clip-a1">
            <name>Atmospheric Flute_Soundscape-12 3.wav</name>
            <duration>100</duration>
            <rate><timebase>24</timebase><ntsc>FALSE</ntsc></rate>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <file id="f-a1">
              <name>Atmospheric Flute_Soundscape-12 3.wav</name>
              <pathurl>file://localhost/G:/Atmospheric%20Flute_Soundscape-12%203.wav</pathurl>
              <rate><timebase>24</timebase><ntsc>FALSE</ntsc></rate>
              <duration>100</duration>
            </file>
            <filter>
              <effect>
                <name>Audio Levels</name>
                <effectid>audiolevels</effectid>
                <effecttype>audiolevels</effecttype>
                <mediatype>audio</mediatype>
                <parameter>
                  <parameterid>level</parameterid>
                  <name>Level</name>
                  <valuemin>0</valuemin>
                  <valuemax>3.98107</valuemax>
                  <valuenumber>1.51000</valuenumber>
                  <value>1.51000</value>
                </parameter>
              </effect>
            </filter>
          </clipitem>
          <transitionitem>
            <start>75</start>
            <end>100</end>
            <alignment>end</alignment>
            <effect>
              <name>Cross Fade (+3dB)</name>
              <effectid>Cross Fade (+3dB)</effectid>
              <effecttype>transition</effecttype>
              <mediatype>audio</mediatype>
            </effect>
          </transitionitem>
        </track>
      </audio>
    </media>
  </sequence>
</xmeml>"""

test_xml = r"c:\Users\Mi5a\VegasDavinciLinkTool\scratch\test_audio_vol.xml"
with open(test_xml, "w", encoding="utf-8") as f:
    f.write(xml_content)

imported_tl = mp.ImportTimelineFromFile(test_xml, {"timelineName": "Test Audio Vol Sync"})
print("Imported audio timeline:", imported_tl)
if imported_tl:
    print("Success! Deleting test timeline now...")
    for j in range(1, proj.GetTimelineCount() + 1):
        tj = proj.GetTimelineByIndex(j)
        if 'Promo Arrow FinalCUTS (VEGAS Sync) 2' in tj.GetName():
            proj.SetCurrentTimeline(tj)
            break
    mp.DeleteTimelines([imported_tl])
    print("Test timeline cleaned up cleanly!")
