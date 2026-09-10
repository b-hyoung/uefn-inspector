"""Binding an @editable slot to an actor in ANOTHER OFPA package (offline).

Structural tests on a hand-built device package (tests/_synth.py) in the form
UEFN writes for stock devices: the slot's sub-object export carries a
`SavedActor` ObjectProperty pointing at the actor import. The same flow is
checked against a real UEFN-written gate actor in test_wire_gate.py.
"""
import struct

import pytest

from uefn_inspector.analysis.verse import verse_bindings
from uefn_inspector.core.properties import decode_properties, property_layout
from uefn_inspector.core.uasset import read_package
from uefn_inspector.edit.add_import import find_import, split_fname
from uefn_inspector.edit.wire import WireError, bind_editable, saved_actor_tag

from _synth import LIGHT_ACTOR_INDEX, device_package, wrapper_form_package

TRIGGER = dict(
    actor_name="Device_InputTrigger_C_UAID_C4EFBBA186F25E0003_1977124380",
    actor_class_package="/CRD_InputTrigger/Device_InputTrigger",
    actor_class_name="Device_InputTrigger_C",
    actor_package_name="/MyProject/__ExternalActors__/MyProject/E/IA/YVW0DKTBG130YA3AMJX908",
)
TAG_LEN = 29   # FName + FName + inner count + size + flags + int32 value


def export_named(pkg, name):
    return next(e for e in pkg.exports if e.object_name == name)


def slot_export(pkg, slot):
    """The `__verse_0x<hash>_<slot>` sub-object export."""
    return next(e for e in pkg.exports
                if e.object_name.startswith("__verse_0x") and e.object_name.endswith("_" + slot))


def saved_actor(pkg, slot):
    v = decode_properties(pkg, slot_export(pkg, slot)).get("SavedActor")
    return int(v[4:]) if v else None


def canonical_tag(pkg, index):
    """The SavedActor tag exactly as the gate file serializes it."""
    return (struct.pack("<ii", pkg.names.index("SavedActor"), 0)
            + struct.pack("<ii", pkg.names.index("ObjectProperty"), 0)
            + struct.pack("<i", 0) + struct.pack("<i", 4) + b"\x00"
            + struct.pack("<i", index))


def assert_wiring(pkg, args, slot):
    """The serialized shape UEFN itself writes for a bound stock-device slot."""
    level = -(next(i for i, m in enumerate(pkg.imports)
                   if m.class_name == "Level" and m.object_name == "PersistentLevel") + 1)
    assert find_import(pkg, class_package="/Script/CoreUObject", class_name="Package",
                       outer_index=0, object_name=args["actor_package_name"]), \
        "Package import for the actor's OFPA package"
    actor = find_import(pkg, class_package=args["actor_class_package"],
                        class_name=args["actor_class_name"], outer_index=level,
                        object_name=args["actor_name"], package_name=args["actor_package_name"])
    assert actor, "actor import under PersistentLevel with PackageName set"
    cls_pkg = find_import(pkg, class_package="/Script/CoreUObject", class_name="Package",
                          outer_index=0, object_name=args["actor_class_package"])
    assert find_import(pkg, class_package="/Script/Engine", class_name="BlueprintGeneratedClass",
                       outer_index=cls_pkg, object_name=args["actor_class_name"])
    # no `<verse_class>_0` wrapper hangs under the actor
    assert not any(m.outer_index == actor for m in pkg.imports)
    assert saved_actor(pkg, slot) == actor
    assert verse_bindings(pkg)[slot] == split_fname(args["actor_name"])[0]
    return actor


def assert_other_exports_intact(before_bytes, before_pkg, after_path, changed):
    """Every export except `changed` keeps its serial bytes; the export map
    and file stay consistent (offsets shifted by the same delta, sizes kept)."""
    after_bytes = after_path.read_bytes()
    after = read_package(after_path)
    assert not after.warnings
    assert [e.object_name for e in after.exports] == [e.object_name for e in before_pkg.exports]
    delta = 0
    for b, a in zip(before_pkg.exports, after.exports):
        if b.serial_offset > 0 and a.serial_offset > 0:
            assert 0 < a.serial_offset and a.serial_offset + a.serial_size <= len(after_bytes)
        if b.object_name == changed:
            delta += a.serial_size - b.serial_size
            continue
        assert a.serial_size == b.serial_size, b.object_name
        assert (after_bytes[a.serial_offset:a.serial_offset + a.serial_size]
                == before_bytes[b.serial_offset:b.serial_offset + b.serial_size]), b.object_name
    # later exports moved by exactly the size change (plus the table growth before them)
    table_growth = (after.exports[0].serial_offset - before_pkg.exports[0].serial_offset)
    for b, a in zip(before_pkg.exports, after.exports):
        expect = b.serial_offset + table_growth
        if b.serial_offset > export_named(before_pkg, changed).serial_offset:
            expect += delta
        assert a.serial_offset == expect, b.object_name
    return after


def test_binding_a_placeholder_slot_adds_the_saved_actor_tag(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    before = read_package(f)
    assert "SavedActor" not in property_layout(before, slot_export(before, "Trigger"))
    assert verse_bindings(before)["Trigger"] is None

    bind_editable(f, "Trigger", **TRIGGER)

    pkg = assert_other_exports_intact(device_package(), before, f, "__verse_0x0000000B_Trigger")
    assert pkg.imports[:before.import_count] == before.imports
    # Package(class pkg) + BGC + Package(actor) + actor — and no wrapper
    assert pkg.import_count == before.import_count + 4
    actor = assert_wiring(pkg, TRIGGER, "Trigger")
    sub = slot_export(pkg, "Trigger")
    assert sub.serial_size == slot_export(before, "Trigger").serial_size + TAG_LEN
    data = f.read_bytes()
    serial = data[sub.serial_offset:sub.serial_offset + sub.serial_size]
    # leading 0 | tag | None | 4-byte tail — identical to the bound Light slot's shape
    assert serial[1:1 + TAG_LEN] == canonical_tag(pkg, actor)
    assert serial == b"\x00" + canonical_tag(pkg, actor) + struct.pack("<ii", pkg.names.index("None"), 0) + b"\x00" * 4
    assert saved_actor(pkg, "Light") == LIGHT_ACTOR_INDEX, "other slot untouched"
    assert (tmp_path / "dev.uasset.bak").read_bytes() == device_package()


def test_binding_a_bound_slot_is_a_same_size_rewrite(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    before = read_package(f)
    assert saved_actor(before, "Light") == LIGHT_ACTOR_INDEX

    bind_editable(f, "Light", **TRIGGER)

    pkg = assert_other_exports_intact(device_package(), before, f, "__verse_0x0000000A_Light")
    assert slot_export(pkg, "Light").serial_size == slot_export(before, "Light").serial_size
    assert_wiring(pkg, TRIGGER, "Light")
    assert verse_bindings(pkg)["Trigger"] is None


def test_bind_editable_is_idempotent_and_reuses_actor_for_second_slot(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    bind_editable(f, "Trigger", **TRIGGER)
    snapshot = f.read_bytes()

    bind_editable(f, "Trigger", **TRIGGER)
    assert f.read_bytes() == snapshot

    bind_editable(f, "Light", **TRIGGER)         # same actor, other slot: no new imports
    pkg = read_package(f)
    assert pkg.import_count == 7 + 4
    assert saved_actor(pkg, "Trigger") == saved_actor(pkg, "Light")


def test_tag_is_synthesized_when_no_bound_slot_exists_in_the_package(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package(bound_light=False))
    before = read_package(f)
    assert "SavedActor" not in before.names
    assert set(verse_bindings(before).values()) == {None}

    bind_editable(f, "Light", **TRIGGER)

    pkg = assert_other_exports_intact(device_package(bound_light=False), before, f,
                                      "__verse_0x0000000A_Light")
    assert pkg.names[:before.name_count] == before.names
    assert "SavedActor" in pkg.names
    actor = assert_wiring(pkg, TRIGGER, "Light")
    data = f.read_bytes()
    sub = slot_export(pkg, "Light")
    assert data[sub.serial_offset + 1:sub.serial_offset + 1 + TAG_LEN] == canonical_tag(pkg, actor)
    # and the cloning path (now that a bound slot exists) yields the same bytes
    assert saved_actor_tag(data, pkg, actor) == canonical_tag(pkg, actor)


def test_bind_editable_unknown_slot_leaves_file_untouched(tmp_path):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())
    with pytest.raises(WireError):
        bind_editable(f, "Nope", **TRIGGER)
    assert f.read_bytes() == device_package()
    assert not (tmp_path / "dev.uasset.bak").exists()


def test_bind_editable_refuses_wrapper_import_slots(tmp_path):
    """A slot whose property points at an import (Verse-class wrapper form)
    is not a stock-device sub-object; refuse rather than guess."""
    f = tmp_path / "dev.uasset"
    f.write_bytes(wrapper_form_package())
    with pytest.raises(WireError, match="wrapper"):
        bind_editable(f, "Light", **TRIGGER)
    assert f.read_bytes() == wrapper_form_package()


def test_bind_editable_rolls_back_on_failure(tmp_path, monkeypatch):
    f = tmp_path / "dev.uasset"
    f.write_bytes(device_package())

    def boom(*a, **k):
        raise RuntimeError("injected")
    monkeypatch.setattr("uefn_inspector.edit.wire.resize_export_data", boom)

    with pytest.raises(RuntimeError, match="injected"):
        bind_editable(f, "Trigger", **TRIGGER)      # imports were already added...
    assert f.read_bytes() == device_package()       # ...and rolled back with them
    assert (tmp_path / "dev.uasset.bak").read_bytes() == device_package()
