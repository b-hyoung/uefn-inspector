"""add_import / bind_editable against a REAL UEFN-written external actor.

Ground truth: the "blackout_light_gate" device actor UEFN saved after five
stock-device @editable slots (Guards, ToggleInput, Light, GunGranter,
GunRemover) were bound in-editor: 45 exports / 104 imports, each slot's
sub-object export carrying a `SavedActor` ObjectProperty that points at the
actor import. It is Epic content, so it is not distributed; place a copy at
tests/fixtures/blackout_gate.uasset (or point UEFN_GATE_FIXTURE at one) to run
these — they skip otherwise.
"""
import os
import shutil
from pathlib import Path

import pytest

from uefn_inspector.analysis.verse import verse_bindings
from uefn_inspector.core.properties import decode_properties, property_layout, property_spans
from uefn_inspector.core.uasset import read_package
from uefn_inspector.edit.add_import import add_import
from uefn_inspector.edit.rebuild import resize_export_data

from test_add_import import check_integrity
from test_wire import (TAG_LEN, TRIGGER, assert_other_exports_intact, assert_wiring,
                       bind_editable, canonical_tag, export_named, saved_actor, slot_export)

GATE = Path(os.environ.get("UEFN_GATE_FIXTURE",
                           Path(__file__).parent / "fixtures" / "blackout_gate.uasset"))
pytestmark = pytest.mark.skipif(not GATE.exists(), reason="ground-truth gate fixture absent")

LIGHT = dict(
    actor_name="Device_PointLight_V2_C_UAID_C4EFBBA186F25E0003_1223763378",
    actor_class_package="/CRD_PointLight/Device_PointLight_V2",
    actor_class_name="Device_PointLight_V2_C",
    actor_package_name="/MyProject/__ExternalActors__/MyProject/0/EC/17YM2L1X4Q8BFYBWSREB2Z",
)
REMOVER = dict(
    actor_name="Device_ItemRemover_V2_C_UAID_C4EFBBA186F25E0003_1977617382",
    actor_class_package="/CRD_ItemRemover/Device_ItemRemover_V2",
    actor_class_name="Device_ItemRemover_V2_C",
    actor_package_name="/MyProject/__ExternalActors__/MyProject/5/AS/VFH02LJKLTFRFK20M6UY4N",
)
NEW_ACTOR = dict(TRIGGER, actor_name="Device_InputTrigger_C_UAID_DEADBEEF00000000_1",
                 actor_package_name="/MyProject/__ExternalActors__/MyProject/0/00/DUMMYPKG")
STOCK_SLOTS = ("Guards", "ToggleInput", "Light", "GunGranter", "GunRemover")


def _gate_props(pkg):
    return decode_properties(pkg, export_named(pkg, "blackout_light_gate"))


def test_ground_truth_shape():
    """What UEFN wrote: the device's slot properties point at sub-object
    EXPORTS; each sub-object's SavedActor points at an actor IMPORT (outer =
    PersistentLevel, PackageName = its OFPA package, which also has a Package
    import). No `<verse_class>_0` wrapper hangs under a stock-device actor."""
    pkg = read_package(GATE)
    assert (pkg.export_count, pkg.import_count, pkg.import_stride) == (45, 104, 40)
    level_i = next(i for i, m in enumerate(pkg.imports) if m.class_name == "Level")
    level = -(level_i + 1)
    props = _gate_props(pkg)
    bindings = verse_bindings(pkg)
    for slot in STOCK_SLOTS:
        (v,) = [v for k, v in props.items() if k.endswith("_" + slot)]
        assert int(v[4:]) > 0, f"{slot}: device property must point at an export"
        actor_i = saved_actor(pkg, slot)
        assert actor_i < 0
        actor = pkg.imports[-actor_i - 1]
        assert actor.outer_index == level and actor.package_name
        assert any(m.class_name == "Package" and m.object_name == actor.package_name
                   for m in pkg.imports)
        assert not any(m.outer_index == actor_i for m in pkg.imports), "no wrapper import"
        assert bindings[slot] == actor.object_name
    assert bindings["ToggleInput"] == "Device_InputTrigger_C_UAID_C4EFBBA186F25E0003"
    assert bindings["Guards"] == "Device_GuardSpawner_V2_C_UAID_C4EFBBA186F2600003"
    # the SavedActor tag bytes, field by field
    data = GATE.read_bytes()
    light = slot_export(pkg, "Light")
    a, b = property_spans(pkg, light)["SavedActor"]
    assert b - a == TAG_LEN
    assert data[a:b] == canonical_tag(pkg, saved_actor(pkg, "Light"))
    assert light.serial_size == 1 + TAG_LEN + 8 + 4       # lead | tag | None | tail


def test_add_import_on_real_uefn_package(tmp_path):
    f = tmp_path / "gate.uasset"
    shutil.copy(GATE, f)
    before = read_package(f)
    level = -(next(i for i, m in enumerate(before.imports) if m.class_name == "Level") + 1)
    props_before = _gate_props(before)
    bindings_before = verse_bindings(before)

    actor = add_import(f, class_package=NEW_ACTOR["actor_class_package"],
                       class_name=NEW_ACTOR["actor_class_name"], outer_index=level,
                       object_name=NEW_ACTOR["actor_name"],
                       package_name=NEW_ACTOR["actor_package_name"])
    pkg = check_integrity(f, before)
    assert pkg.import_count == before.import_count + 1
    assert actor == -pkg.import_count
    assert pkg.imports[-1].full_name == NEW_ACTOR["actor_name"]
    assert _gate_props(pkg) == props_before
    assert verse_bindings(pkg) == bindings_before


def test_rebinding_to_the_current_actor_is_a_no_op(tmp_path):
    """(i) Our serialized shape equals UEFN's: re-binding ToggleInput to the
    actor it is already bound to reuses every import and changes no byte."""
    f = tmp_path / "gate.uasset"
    shutil.copy(GATE, f)
    bind_editable(f, "ToggleInput", **TRIGGER)
    assert f.read_bytes() == GATE.read_bytes()


def test_rebinding_to_another_existing_actor_changes_only_the_index(tmp_path):
    """(ii) Both actors are already imported: only the 4-byte SavedActor
    value of the ToggleInput sub-object changes."""
    f = tmp_path / "gate.uasset"
    shutil.copy(GATE, f)
    before = read_package(f)
    data0 = GATE.read_bytes()
    voff = property_layout(before, slot_export(before, "ToggleInput"))["SavedActor"][0]

    bind_editable(f, "ToggleInput", **LIGHT)

    data = f.read_bytes()
    assert len(data) == len(data0)
    changed = [i for i in range(len(data)) if data[i] != data0[i]]
    assert changed and set(changed) <= set(range(voff, voff + 4))   # -21 -> -24: low byte only
    pkg = read_package(f)
    assert saved_actor(pkg, "ToggleInput") == saved_actor(pkg, "Light")
    assert verse_bindings(pkg)["ToggleInput"] == "Device_PointLight_V2_C_UAID_C4EFBBA186F25E0003"


def test_binding_a_placeholder_slot_reproduces_uefn_bytes(tmp_path):
    """(iii) Every stock slot in the gate file is bound, so build the fresh
    placeholder from the real one: strip GunRemover's SavedActor tag (it then
    reads as unbound, `00 | None | 0000`), bind it back, and the whole file
    must equal what UEFN wrote."""
    data0 = GATE.read_bytes()
    gt = read_package(GATE)
    gi = [e.object_name for e in gt.exports].index("__verse_0x184C800C_GunRemover")
    e = gt.exports[gi]
    a, b = property_spans(gt, e)["SavedActor"]
    serial = data0[e.serial_offset:e.serial_offset + e.serial_size]
    stripped = serial[:a - e.serial_offset] + serial[b - e.serial_offset:]
    assert len(stripped) == 13

    f = tmp_path / "gate.uasset"
    f.write_bytes(bytes(resize_export_data(data0, gt, gi, stripped)))
    before = read_package(f)
    assert not before.warnings
    assert verse_bindings(before)["GunRemover"] is None
    assert "SavedActor" not in property_layout(before, before.exports[gi])
    placeholder = f.read_bytes()

    bind_editable(f, "GunRemover", **REMOVER)

    pkg = assert_other_exports_intact(placeholder, before, f, "__verse_0x184C800C_GunRemover")
    assert pkg.exports[gi].serial_size == 13 + TAG_LEN
    assert verse_bindings(pkg)["GunRemover"] == "Device_ItemRemover_V2_C_UAID_C4EFBBA186F25E0003"
    assert f.read_bytes() == data0


def test_binding_to_a_new_actor(tmp_path):
    f = tmp_path / "gate.uasset"
    shutil.copy(GATE, f)
    before = read_package(f)
    others = {s: saved_actor(before, s) for s in ("Guards", "Light", "GunGranter", "GunRemover")}
    bind_editable(f, "ToggleInput", **NEW_ACTOR)
    pkg = check_integrity(f, before)
    # class imports already exist: only Package(actor) + actor are new
    assert pkg.import_count == before.import_count + 2
    actor = assert_wiring(pkg, NEW_ACTOR, "ToggleInput")
    assert actor == -pkg.import_count
    assert verse_bindings(pkg)["ToggleInput"] == "Device_InputTrigger_C_UAID_DEADBEEF00000000"
    for slot, idx in others.items():
        assert saved_actor(pkg, slot) == idx                          # untouched
