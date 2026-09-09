from pathlib import Path

from uefn_inspector.uasset import read_package
from uefn_inspector.verse import verse_bindings
from uefn_inspector.verse_source import cross_reference, parse_verse

FIX = Path(__file__).parent / "fixtures"


def test_parse_class_and_editables():
    info = parse_verse((FIX / "knife_sense.verse").read_text(encoding="utf-8"))
    assert info["class_name"] == "knife_sense"
    assert info["base_class"] == "creative_device"
    slots = {e["name"]: e["type"] for e in info["editables"]}
    assert slots["KnifeDesign"] == "class_designer_device"
    assert slots["HeartFar"] == "audio_player_device"
    assert slots["RSense"] == "float"


def test_parse_functions():
    info = parse_verse((FIX / "gun_light.verse").read_text(encoding="utf-8"))
    assert info["class_name"] == "gun_light"
    assert "OnBegin" in info["functions"]


def test_cross_reference_detects_unwired_slot():
    # knife_sense.verse declares HeartMid; the placed device (.uasset) wires
    # only KnifeDesign/HeartFar/HeartNear -> HeartMid is unwired (silent bug).
    info = parse_verse((FIX / "knife_sense.verse").read_text(encoding="utf-8"))
    bindings = verse_bindings(read_package(FIX / "versedevice.uasset"))
    xref = cross_reference(info, bindings)
    assert "HeartMid" in xref["unwired"]
    assert "HeartFar" in xref["wired"]
    assert "KnifeDesign" in xref["wired"]
