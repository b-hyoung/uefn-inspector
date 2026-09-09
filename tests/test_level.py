from pathlib import Path

from uefn_inspector.level import inspect_actor

FIXTURE = Path(__file__).parent / "fixtures" / "audioplayer.uasset"


def test_inspect_audioplayer_actor():
    actor = inspect_actor(FIXTURE)
    assert actor.device_class == "Device_CRD_AudioPlayer_C"
    assert any("Heartbeat_Near" in ref for ref in actor.asset_refs)
