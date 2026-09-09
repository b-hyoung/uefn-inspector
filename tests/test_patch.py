import shutil
from pathlib import Path

from uefn_inspector.patch import patch_scalar_file
from uefn_inspector.properties import decode_properties
from uefn_inspector.uasset import read_package

SMALL = Path(__file__).parent / "fixtures" / "small.uasset"


def test_patch_scalar_file_with_backup(tmp_path):
    target = tmp_path / "t.uasset"
    shutil.copy(SMALL, target)

    bak = patch_scalar_file(target, "StaticMeshComponent0",
                            "CachedMaxDrawDistance", 42.0)

    assert bak.exists()  # backup taken
    pkg = read_package(target)
    smc = next(e for e in pkg.exports if e.object_name == "StaticMeshComponent0")
    assert decode_properties(pkg, smc)["CachedMaxDrawDistance"] == 42.0
