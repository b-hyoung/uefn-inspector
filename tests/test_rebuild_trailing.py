"""Size-changing edits must keep every *file-internal offset* consistent.

The package summary carries several offsets after the import-map pointer
(depends map, asset-registry, bulk-data start, ...). Any of them that points at
or beyond the edited region must shift by the same delta, or UE will read
garbage. Offsets that live *before* the edited region must not move.
"""
from pathlib import Path

from uefn_inspector.core.properties import decode_properties
from uefn_inspector.core.uasset import read_package
from uefn_inspector.edit.rebuild import resize_export_data, trailing_offsets

SMALL = Path(__file__).parent / "fixtures" / "small.uasset"


def test_trailing_offsets_are_discovered():
    pkg = read_package(SMALL)
    offs = trailing_offsets(SMALL.read_bytes(), pkg)
    # every reported entry is a plausible in-file offset
    assert offs
    n = SMALL.stat().st_size
    for pos, value in offs:
        assert 0 < value <= n
        assert pkg.trailing_summary_pos <= pos < pkg.name_offset


def test_growth_shifts_only_offsets_after_the_edit():
    data = SMALL.read_bytes()
    pkg = read_package(SMALL)
    before = dict(trailing_offsets(data, pkg))

    e0 = pkg.exports[0]  # first export -> everything after it moves
    grown = data[e0.serial_offset:e0.serial_offset + e0.serial_size] + b"\x00" * 8
    out = resize_export_data(data, pkg, 0, grown)

    pkg2 = read_package_bytes(out)
    after = dict(trailing_offsets(bytes(out), pkg2))

    for pos, old in before.items():
        new = after[pos]
        expected = old + 8 if old > e0.serial_offset else old
        assert new == expected, f"offset at {pos}: {old} -> {new}, expected {expected}"


def test_grown_package_still_decodes(tmp_path):
    data = SMALL.read_bytes()
    pkg = read_package(SMALL)
    smc = next(e for e in pkg.exports if e.object_name == "StaticMeshComponent0")
    expected = decode_properties(pkg, smc)["CachedMaxDrawDistance"]

    e0 = pkg.exports[0]
    grown = data[e0.serial_offset:e0.serial_offset + e0.serial_size] + b"\x00" * 8
    out = resize_export_data(data, pkg, 0, grown)

    f = tmp_path / "grown.uasset"
    f.write_bytes(bytes(out))
    pkg2 = read_package(f)
    smc2 = next(e for e in pkg2.exports if e.object_name == "StaticMeshComponent0")
    assert decode_properties(pkg2, smc2)["CachedMaxDrawDistance"] == expected


def read_package_bytes(buf):
    """Helper: parse an in-memory package via a temp file."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".uasset", delete=False) as fh:
        fh.write(bytes(buf))
        name = fh.name
    return read_package(name)
