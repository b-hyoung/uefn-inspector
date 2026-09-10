"""Adding an IMPORT row (cross-package reference) — size-changing edit.

Structural tests on a hand-built package (tests/_synth.py); the same edit is
exercised against a real UEFN-written external actor in test_wire_gate.py.
"""
import pytest

from uefn_inspector.core.properties import decode_properties
from uefn_inspector.core.uasset import read_package
from uefn_inspector.edit.add_import import AddImportError, add_import, split_fname

from _synth import device_package

ACTOR = dict(class_package="/CRD_InputTrigger/Device_InputTrigger",
             class_name="Device_InputTrigger_C",
             object_name="Device_InputTrigger_C_UAID_C4EFBBA186F25E0003_1977124380",
             package_name="/MyProject/__ExternalActors__/MyProject/E/IA/YVW0DKTBG130YA3AMJX908")


def check_integrity(path, before):
    """Re-read `path` and assert everything that existed before is unchanged."""
    pkg = read_package(path)
    n = path.stat().st_size
    assert not pkg.warnings
    assert pkg.import_count == len(pkg.imports)
    assert pkg.imports[:before.import_count] == before.imports   # decoded form unchanged
    assert pkg.names[:before.name_count] == before.names
    assert [e.object_name for e in pkg.exports] == [e.object_name for e in before.exports]
    for e in pkg.exports:
        assert 0 < e.serial_offset and e.serial_offset + e.serial_size <= n
    return pkg


def test_split_fname_follows_ue_rule():
    assert split_fname("input_trigger_device_0") == ("input_trigger_device", 1)
    assert split_fname("X_UAID_C4EFBBA186F25E0003_1977124380") == ("X_UAID_C4EFBBA186F25E0003", 1977124381)
    assert split_fname("Device_GuardSpawner_V2_C") == ("Device_GuardSpawner_V2_C", 0)
    assert split_fname("foo_007") == ("foo_007", 0)      # leading zero: not a number
    assert split_fname("StaticMeshComponent0") == ("StaticMeshComponent0", 0)


def test_reader_parses_full_import_row(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    pkg = read_package(f)
    assert pkg.import_stride == 40
    level = pkg.imports[2]
    assert (level.class_name, level.object_name, level.outer_index) == ("Level", "PersistentLevel", -2)
    assert level.package_name == "" and level.optional is False and level.object_number == 0
    assert level.full_name == "PersistentLevel"


def test_add_import_appends_row_and_keeps_package_consistent(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    before = read_package(f)
    gate = next(e for e in before.exports if e.object_name == "my_gate")
    props_before = decode_properties(before, gate)

    idx = add_import(f, outer_index=-3, **ACTOR)

    assert idx == -(before.import_count + 1)
    pkg = check_integrity(f, before)
    assert pkg.import_count == before.import_count + 1
    new = pkg.imports[-1]
    assert (new.class_package, new.class_name, new.outer_index) == (
        ACTOR["class_package"], ACTOR["class_name"], -3)
    assert new.object_name == "Device_InputTrigger_C_UAID_C4EFBBA186F25E0003"
    assert new.object_number == 1977124381
    assert new.full_name == ACTOR["object_name"]
    assert new.package_name == ACTOR["package_name"]
    assert new.optional is False
    # names: only the missing ones were appended, at the end
    assert pkg.name_count == before.name_count + 4
    # property data survived the move
    gate2 = next(e for e in pkg.exports if e.object_name == "my_gate")
    assert decode_properties(pkg, gate2) == props_before
    # backup is the original
    assert (tmp_path / "dev.uasset.bak").read_bytes() == device_package()


def test_add_import_reuses_names_and_is_idempotent(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    before = read_package(f)

    # identical row exists -> reused, file untouched
    idx = add_import(f, class_package="/Script/CoreUObject", class_name="Package",
                     outer_index=0, object_name="/MyProject/_Verse", package_name="")
    assert idx == -4
    assert f.read_bytes() == device_package()

    # every FName already exists -> no name-table growth, just one row
    idx = add_import(f, class_package="/Script/Engine", class_name="World",
                     outer_index=-1, object_name="PersistentLevel_0")
    pkg = check_integrity(f, before)
    assert pkg.name_count == before.name_count
    assert pkg.imports[-1].object_number == 1 and pkg.imports[-1].full_name == "PersistentLevel_0"
    snapshot = f.read_bytes()
    assert add_import(f, class_package="/Script/Engine", class_name="World",
                      outer_index=-1, object_name="PersistentLevel_0") == idx
    assert f.read_bytes() == snapshot


def test_add_import_rejects_unknown_outer(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    with pytest.raises(AddImportError):
        add_import(f, outer_index=-99, **ACTOR)
    assert f.read_bytes() == device_package()
