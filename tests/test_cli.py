from pathlib import Path

from uefn_inspector.cli import run

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_cli_run_reports_device_counts():
    report = run(LEVEL_DIR)
    assert report["actor_count"] == 3
    assert report["devices"]["Device_CRD_AudioPlayer_C"] == 1
    assert report["devices"]["GrayBox_Solid_Wall_C"] == 1
