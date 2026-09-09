import shutil
from pathlib import Path

from uefn_inspector.properties import decode_properties
from uefn_inspector.uasset import read_package
from uefn_inspector.write import set_scalar

SMALL = Path(__file__).parent / "fixtures" / "small.uasset"


def test_offline_scalar_write_roundtrip(tmp_path):
    # copy — never touch the original
    copy = tmp_path / "copy.uasset"
    shutil.copy(SMALL, copy)
    data = bytearray(copy.read_bytes())

    pkg = read_package(copy)
    smc = next(e for e in pkg.exports if e.object_name == "StaticMeshComponent0")

    set_scalar(data, pkg, smc, "CachedMaxDrawDistance", 999.0)
    copy.write_bytes(bytes(data))

    pkg2 = read_package(copy)
    smc2 = next(e for e in pkg2.exports if e.object_name == "StaticMeshComponent0")
    assert decode_properties(pkg2, smc2)["CachedMaxDrawDistance"] == 999.0
    assert len(pkg2.exports) == len(pkg.exports)  # package still intact
