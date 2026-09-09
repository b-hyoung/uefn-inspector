from pathlib import Path

from uefn_inspector.core.properties import decode_properties
from uefn_inspector.edit.rebuild import resize_export_data
from uefn_inspector.core.uasset import read_package

SMALL = Path(__file__).parent / "fixtures" / "small.uasset"


def test_identity_resize_is_byte_identical():
    data = bytearray(SMALL.read_bytes())
    pkg = read_package(SMALL)
    e = pkg.exports[0]
    same = bytes(data[e.serial_offset:e.serial_offset + e.serial_size])
    out = resize_export_data(data, pkg, 0, same)
    assert bytes(out) == bytes(SMALL.read_bytes())


def test_resize_fixes_later_export_offsets(tmp_path):
    data = SMALL.read_bytes()
    pkg = read_package(SMALL)
    smc = next(e for e in pkg.exports if e.object_name == "StaticMeshComponent0")
    before = decode_properties(pkg, smc)["CachedMaxDrawDistance"]

    e0 = pkg.exports[0]
    grown = bytes(data[e0.serial_offset:e0.serial_offset + e0.serial_size]) + b"\x00" * 8
    out = resize_export_data(data, pkg, 0, grown)

    tmp = tmp_path / "r.uasset"
    tmp.write_bytes(bytes(out))
    pkg2 = read_package(tmp)
    assert pkg2.export_count == pkg.export_count
    smc2 = next(e for e in pkg2.exports if e.object_name == "StaticMeshComponent0")
    # later export still decodes correctly -> its SerialOffset was fixed
    assert decode_properties(pkg2, smc2)["CachedMaxDrawDistance"] == before
