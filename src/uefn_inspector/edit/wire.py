"""Wire an @editable device slot to an actor in ANOTHER OFPA package (offline).

Reproduces what UEFN writes when a stock-device slot is bound in the editor
GUI (ground truth: the "blackout_light_gate" external actor saved by UEFN with
five slots bound). The device export's `__verse_0x<hash>_<Slot>` ObjectProperty
points at a SUB-OBJECT EXPORT of the same name, and the binding lives on that
sub-object as a `SavedActor` ObjectProperty whose value is the target ACTOR
import. Per bound actor the file holds:

  * `Package` import   — class Package, outer 0, name = the actor's OFPA
                         package path
  * the actor import   — class <actor_class_name>, outer = PersistentLevel,
                         PackageName = that same OFPA path
  * class imports      — BlueprintGeneratedClass <actor_class_name> under a
                         Package import of the class's package (UE harvests
                         every import's class)

There is NO `<verse_class>_0` wrapper import for stock devices: that form
fails to resolve on level reload and UEFN reverts the slot to its
placeholder. (Slots typed with a *user* Verse class — e.g. a `tuning` class
placed as its own VerseDevice — still use a wrapper import; not handled here.)

Serialized `SavedActor` tag, byte-for-byte as in the gate file (UE5.4
FPropertyTag with FPropertyTypeName, no ArrayIndex/Guid):

    FName  SavedActor      (name idx int32, number 0)          8
    FName  ObjectProperty  (type-name root, number 0)          8
    int32  0               (FPropertyTypeName inner count)     4
    int32  4               (Size)                              4
    uint8  0               (PropertyTagFlags)                  1
    int32  <actor import>  (FPackageIndex, negative)           4   = 29 bytes

A fresh placeholder sub-object serializes only non-default properties, so it
has no `SavedActor` tag at all (`00 | None | 00000000`); binding it inserts
the tag right before the terminating "None" and resizes the export.

⚠️ 구조 검증됨 / UEFN 수용: 에디터 세션 검증 진행 중. Work on a copy, keep the .bak.
"""
from __future__ import annotations

import re
import shutil
import struct
from pathlib import Path

from ..core.properties import (decode_properties, property_layout, property_spans,
                               property_terminator)
from ..core.uasset import ObjectExport, Package, read_package
from .add_import import add_import, ensure_names
from .rebuild import resize_export_data
from .write import set_object_ref

SAVED_ACTOR = "SavedActor"
_OBJECT_PROPERTY = "ObjectProperty"


class WireError(RuntimeError):
    pass


def _level_import(pkg: Package) -> int:
    for k, imp in enumerate(pkg.imports):
        if imp.class_name == "Level" and imp.object_name == "PersistentLevel":
            return -(k + 1)
    raise WireError("no PersistentLevel import (class Level) — not a placed actor package?")


def _obj_index(value) -> int | None:
    if isinstance(value, str) and value.startswith("obj:"):
        return int(value[4:])
    return None


def _slot_export(pkg: Package, slot: str) -> int:
    """Export index (0-based) of the `__verse_0x<hash>_<slot>` sub-object the
    device's slot property points at."""
    pat = re.compile(r"__verse_0x[0-9A-Fa-f]+_" + re.escape(slot) + r"$")
    for e in pkg.exports:
        for prop, value in decode_properties(pkg, e).items():
            if not pat.match(prop):
                continue
            idx = _obj_index(value)
            if idx is None:
                raise WireError(f"slot {slot} is not an ObjectProperty ({value!r})")
            if idx > 0 and idx - 1 < len(pkg.exports):
                return idx - 1
            if idx < 0:
                target = pkg.imports[-idx - 1]
                raise WireError(
                    f"slot {slot} points at import {target.full_name!r} "
                    f"(class {target.class_name}) — a Verse-class wrapper binding, "
                    "not a stock-device sub-object; unsupported")
            raise WireError(f"slot {slot} has no sub-object export (value {value!r})")
    raise WireError(f"slot property not found on any export: {slot}")


def saved_actor_tag(data: bytes, pkg: Package, package_index: int) -> bytes:
    """The serialized `SavedActor` ObjectProperty tag pointing at `package_index`.

    Cloned from an existing bound slot in the same package when there is one
    (only the 4-byte value differs); otherwise synthesized in exactly the
    layout documented above. Both names must already be in the name table.
    """
    for e in pkg.exports:
        layout = property_layout(pkg, e).get(SAVED_ACTOR)
        if not layout or layout[2] != _OBJECT_PROPERTY or layout[1] != 4:
            continue
        voff = layout[0]
        a, b = property_spans(pkg, e)[SAVED_ACTOR]
        tag = bytearray(data[a:b])
        struct.pack_into("<i", tag, voff - a, package_index)
        return bytes(tag)
    names = pkg.names
    return (struct.pack("<ii", names.index(SAVED_ACTOR), 0)
            + struct.pack("<ii", names.index(_OBJECT_PROPERTY), 0)
            + struct.pack("<i", 0)            # FPropertyTypeName: no inner types
            + struct.pack("<i", 4)            # Size
            + b"\x00"                         # PropertyTagFlags
            + struct.pack("<i", package_index))


def _insert_saved_actor(p: Path, slot_i: int, package_index: int) -> None:
    """Add a `SavedActor` tag to a placeholder sub-object (size-changing)."""
    ensure_names(p, [SAVED_ACTOR, _OBJECT_PROPERTY], backup=False)
    pkg = read_package(p)
    sub = pkg.exports[slot_i]
    term = property_terminator(pkg, sub)
    if term is None:
        raise WireError(f"property list of {sub.object_name} does not terminate cleanly")
    data = bytes(p.read_bytes())
    tag = saved_actor_tag(data, pkg, package_index)
    serial = data[sub.serial_offset:sub.serial_offset + sub.serial_size]
    rel = term - sub.serial_offset
    out = resize_export_data(data, pkg, slot_i, serial[:rel] + tag + serial[rel:])
    p.write_bytes(bytes(out))


def bind_editable(path: str | Path, slot: str, *, actor_name: str,
                  actor_class_package: str, actor_class_name: str,
                  actor_package_name: str) -> None:
    """Point @editable `slot` at `actor_name` living in `actor_package_name`.

    Idempotent: existing identical imports are reused; re-binding to the
    current actor changes no byte. One backup (.bak) is taken before the
    first change and restored if any step fails.
    """
    p = Path(path)
    pkg = read_package(p)
    _slot_export(pkg, slot)                # fail early, before touching the file
    level = _level_import(pkg)
    bak = p.with_suffix(p.suffix + ".bak")
    shutil.copy(p, bak)
    try:
        def pkg_import(name: str) -> int:
            return add_import(p, class_package="/Script/CoreUObject", class_name="Package",
                              outer_index=0, object_name=name, backup=False)

        # class import (harvested by UE for every import's class)
        add_import(p, class_package="/Script/Engine", class_name="BlueprintGeneratedClass",
                   outer_index=pkg_import(actor_class_package),
                   object_name=actor_class_name, backup=False)
        # the actor (OFPA: Package import + PackageName on the actor row)
        pkg_import(actor_package_name)
        actor = add_import(p, class_package=actor_class_package, class_name=actor_class_name,
                           outer_index=level, object_name=actor_name,
                           package_name=actor_package_name, backup=False)

        pkg = read_package(p)
        slot_i = _slot_export(pkg, slot)
        sub = pkg.exports[slot_i]
        if SAVED_ACTOR in property_layout(pkg, sub):
            data = bytearray(p.read_bytes())            # (a) bound before: same-size
            set_object_ref(data, pkg, sub, SAVED_ACTOR, actor)
            p.write_bytes(bytes(data))
        else:
            _insert_saved_actor(p, slot_i, actor)       # (b) placeholder: add the tag

        check = read_package(p)
        ok = (not check.warnings
              and [e.object_name for e in check.exports] == [e.object_name for e in pkg.exports]
              and decode_properties(check, check.exports[slot_i]).get(SAVED_ACTOR) == f"obj:{actor}")
        if not ok:
            raise WireError("result does not read back as expected — rolled back")
    except Exception:
        shutil.copy(bak, p)
        raise
