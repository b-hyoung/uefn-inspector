from pathlib import Path

from uefn_inspector.properties import decode_properties
from uefn_inspector.uasset import read_package
from uefn_inspector.verse import verse_bindings

AUDIO = Path(__file__).parent / "fixtures" / "audioplayer.uasset"
VERSE = Path(__file__).parent / "fixtures" / "versedevice.uasset"


def test_device_setting_value_decodes():
    # The value the original session could NOT read via MCP/reflection.
    pkg = read_package(AUDIO)
    main = next(e for e in pkg.exports if "_UAID_" in e.object_name)
    props = decode_properties(pkg, main)
    assert props.get("Can Be Heard By") == "ECreativeAudioPlayerTarget::NewEnumerator3"


def test_verse_editable_bindings_decode():
    pkg = read_package(VERSE)
    b = verse_bindings(pkg)
    assert "KnifeDesign" in b and "HeartFar" in b and "HeartNear" in b
