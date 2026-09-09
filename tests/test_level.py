from pathlib import Path

from uefn_inspector.level import inspect_actor, inspect_level

FIXTURE = Path(__file__).parent / "fixtures" / "audioplayer.uasset"
LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


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
