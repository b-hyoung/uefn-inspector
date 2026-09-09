from pathlib import Path

from uefn_inspector.properties import decode_properties
from uefn_inspector.uasset import read_package

SMALL = Path(__file__).parent / "fixtures" / "small.uasset"


def _smc():
    pkg = read_package(SMALL)
    smc = next(e for e in pkg.exports if e.object_name == "StaticMeshComponent0")
    return decode_properties(pkg, smc)


def test_decode_standard_scalar_property():
    props = _smc()
    assert isinstance(props.get("CachedMaxDrawDistance"), float)


def test_decode_transform_vector_as_three_numbers():
    props = _smc()
    loc = props.get("RelativeLocation")
    assert isinstance(loc, tuple) and len(loc) == 3
    assert all(isinstance(x, float) for x in loc)
