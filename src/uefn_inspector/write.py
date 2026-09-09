"""Offline in-place value writes (same-size only — no offset shifts).

Structurally safe: patching a fixed-width scalar does not move any bytes, so
the name table / export offsets / header stay valid. UEFN *acceptance* of a
modified file (name hashes, publish validation) is NOT verified here — that is
the live spike (destructive, needs approval). Callers pass a bytearray copy;
this never touches the original file.
"""
from __future__ import annotations

import struct

from .properties import property_layout
from .uasset import ObjectExport, Package


class WriteError(Exception):
    pass


def _layout_entry(pkg: Package, export: ObjectExport, prop: str):
    layout = property_layout(pkg, export)
    if prop not in layout:
        raise WriteError(f"property not found: {prop}")
    return layout[prop]


def set_scalar(data: bytearray, pkg: Package, export: ObjectExport,
               prop_name: str, value) -> None:
    """Patch a Float/Int scalar property in place (same byte width)."""
    layout = property_layout(pkg, export)
    if prop_name not in layout:
        raise WriteError(f"property not found: {prop_name}")
    offset, size, root = layout[prop_name]
    if root == "FloatProperty" and size == 4:
        struct.pack_into("<f", data, offset, float(value))
    elif root == "DoubleProperty" and size == 8:
        struct.pack_into("<d", data, offset, float(value))
    elif root in ("IntProperty", "Int32Property") and size == 4:
        struct.pack_into("<i", data, offset, int(value))
    else:
        raise WriteError(f"unsupported for in-place write: {root} size={size}")


def set_enum(data: bytearray, pkg: Package, export: ObjectExport,
             prop: str, enum_value_name: str) -> None:
    """Set an Enum/Byte(enum) property to a different enumerator (FName, 8 bytes).

    The target enumerator name must ALREADY exist in the package name table
    (same-size write only — no name-table growth). Otherwise raises.
    """
    offset, size, root = _layout_entry(pkg, export, prop)
    if root not in ("EnumProperty", "ByteProperty"):
        raise WriteError(f"{prop} is {root}, not an enum")
    if enum_value_name not in pkg.names:
        raise WriteError(f"enum value '{enum_value_name}' not in name table "
                         f"(same-size write needs it to already exist)")
    idx = pkg.names.index(enum_value_name)
    struct.pack_into("<ii", data, offset, idx, 0)  # FName: name_index, number


def set_object_ref(data: bytearray, pkg: Package, export: ObjectExport,
                   prop: str, package_index: int) -> None:
    """Rewire an ObjectProperty (e.g. an @editable binding's SavedActor) to a
    different FPackageIndex (int32, 4 bytes). Positive = export, negative =
    import; the target must already exist in the package."""
    offset, size, root = _layout_entry(pkg, export, prop)
    if root != "ObjectProperty":
        raise WriteError(f"{prop} is {root}, not an object reference")
    n_exports, n_imports = len(pkg.exports), len(pkg.imports)
    if not (0 < package_index <= n_exports or -n_imports <= package_index < 0):
        raise WriteError(f"package index {package_index} out of range")
    struct.pack_into("<i", data, offset, package_index)
