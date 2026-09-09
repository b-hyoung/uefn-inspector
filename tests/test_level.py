from pathlib import Path

from uefn_inspector.level import (
    Level,
    audit_level,
    diff_levels,
    inspect_actor,
    inspect_level,
)

FIXTURE = Path(__file__).parent / "fixtures" / "audioplayer.uasset"
LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_inspect_actor_decodes_location():
    wall = LEVEL_DIR / "wall.uasset"
    actor = inspect_actor(wall)
    assert isinstance(actor.location, tuple) and len(actor.location) == 3
    assert all(isinstance(x, float) for x in actor.location)


def test_inspect_audioplayer_actor():
    actor = inspect_actor(FIXTURE)
    assert actor.device_class == "Device_CRD_AudioPlayer_C"
    assert any("Heartbeat_Near" in ref for ref in actor.asset_refs)


def test_inspect_level_aggregates_actors():
    level = inspect_level(LEVEL_DIR)
    assert len(level.actors) == 3
    classes = {a.device_class for a in level.actors}
    assert "Device_CRD_AudioPlayer_C" in classes
    assert "GrayBox_Solid_Wall_C" in classes
    assert "Device_ClassSelector_V2_C" in classes


def test_audit_reports_counts_and_keys():
    rep = audit_level(LEVEL_DIR)
    assert rep["device_counts"]
    assert "duplicate_names" in rep
    assert "broken_refs" in rep


def test_diff_same_level_is_empty():
    a = inspect_level(LEVEL_DIR)
    d = diff_levels(a, a)
    assert d["added"] == {} and d["removed"] == {}


def test_diff_detects_removal():
    a = inspect_level(LEVEL_DIR)
    b = Level(actors=a.actors[:-1])
    d = diff_levels(a, b)
    assert d["removed"]
