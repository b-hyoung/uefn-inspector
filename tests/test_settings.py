from pathlib import Path

from uefn_inspector.query import list_settings
from uefn_inspector.uasset import read_package

FIXTURE = Path(__file__).parent / "fixtures" / "audioplayer.uasset"


def test_list_settings_surfaces_names_and_enums():
    pkg = read_package(FIXTURE)
    s = list_settings(pkg)
    assert "Can Be Heard By" in s["display_settings"]
    assert "ECreativeAudioPlayerTarget" in s["enums"]
    # enum values (with ::) are not enum types
    assert "ECreativeAudioPlayerTarget::NewEnumerator3" not in s["enums"]
