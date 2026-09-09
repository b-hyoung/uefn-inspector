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
