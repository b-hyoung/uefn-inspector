import os

from uefn_inspector.uasset import read_package


def test_read_package_graceful_on_truncated_file(tmp_path):
    f = tmp_path / "tiny.uasset"
    f.write_bytes(b"\x00" * 8)  # shorter than the fixed header
    pkg = read_package(f)       # must not raise
    assert pkg.exports == []
    assert pkg.warnings


def test_read_package_graceful_on_garbage(tmp_path):
    f = tmp_path / "rnd.uasset"
    f.write_bytes(os.urandom(128))
    pkg = read_package(f)       # must not raise
    assert pkg.exports == []
