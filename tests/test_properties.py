from pathlib import Path

from uefn_inspector.properties import decode_properties, property_layout
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


def test_bool_and_str_properties_decode():
    # regression: bool value lives in PropertyTagFlags (0x10), str in value region
    pkg = read_package(SMALL)
    got_bool = got_str = False
    for e in pkg.exports:
        for name, v in decode_properties(pkg, e).items():
            lay = property_layout(pkg, e).get(name)
            if lay and lay[2] == "BoolProperty":
                assert isinstance(v, bool)
                got_bool = True
            if lay and lay[2] == "StrProperty" and v:
                assert isinstance(v, str)
                got_str = True
    assert got_bool and got_str
