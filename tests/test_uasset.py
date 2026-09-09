from pathlib import Path

from uefn_inspector.uasset import read_package

FIXTURE = Path(__file__).parent / "fixtures" / "audioplayer.uasset"

UE_PACKAGE_MAGIC = 0x9E2A83C1


def test_reads_package_magic_and_ue5_version():
    pkg = read_package(FIXTURE)
    assert pkg.tag == UE_PACKAGE_MAGIC
    assert pkg.file_version_ue4 == 522
    assert pkg.file_version_ue5 == 1018


def test_name_table_contains_device_class_and_sound():
    pkg = read_package(FIXTURE)
    assert len(pkg.names) == pkg.name_count
    assert "Device_CRD_AudioPlayer_C" in pkg.names
    assert "Heartbeat_Near" in pkg.names
