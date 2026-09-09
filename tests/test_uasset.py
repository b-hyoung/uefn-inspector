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


def test_import_map_resolves_object_references():
    pkg = read_package(FIXTURE)
    assert len(pkg.imports) == pkg.import_count
    names = {imp.object_name for imp in pkg.imports}
    assert "Device_CRD_AudioPlayer_C" in names


def test_export_map_has_placed_actor_with_serial_region():
    pkg = read_package(FIXTURE)
    assert len(pkg.exports) == pkg.export_count
    filesize = FIXTURE.stat().st_size
    main = next(e for e in pkg.exports if "_UAID_" in e.object_name)
    assert main.object_name.startswith("Device_CRD_AudioPlayer_C")
    assert main.serial_size > 0
    assert 0 < main.serial_offset < filesize
    assert main.serial_offset + main.serial_size <= filesize
