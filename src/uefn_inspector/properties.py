"""Tagged-property value decoding (UE5 v1012+ / FPropertyTypeName format).

Layout per property (confirmed against UEFN v1018 assets, cf. CUE4Parse):

    Name            FName (idx int32 + number int32)
    TypeName        FPropertyTypeName = FName + InnerCount int32 + children (recursive)
    Size            int32
    PropertyTagFlags uint8
        flags & 0x01 -> ArrayIndex int32
        flags & 0x02 -> PropertyGuid (16 bytes)
    Value           `Size` bytes

Only standard scalar/struct values are decoded; anything else is kept raw.
Verse-VM device settings (GUID-wrapped) are NOT standard tags and stay opaque.
"""
from __future__ import annotations

import struct
from pathlib import Path

from .uasset import ObjectExport, Package

_MAX_INNER = 6
_MAX_DEPTH = 6
_MAX_LEAD = 6  # bytes of leading data to probe before the property list


class _Bad(Exception):
    pass


def _i32(d: bytes, o: int) -> int:
    return struct.unpack_from("<i", d, o)[0]


def _fname(d: bytes, o: int, names: list[str]) -> tuple[str, int]:
    if o + 8 > len(d):
        raise _Bad
    ix = _i32(d, o)
    if not (0 <= ix < len(names)):
        raise _Bad
    return names[ix], o + 8


def _typename(d: bytes, o: int, names: list[str], depth: int = 0) -> tuple[str, list, int]:
    """FPropertyTypeName node -> (root_name, children, next_offset)."""
    if depth > _MAX_DEPTH:
        raise _Bad
    root, o = _fname(d, o, names)
    if o + 4 > len(d):
        raise _Bad
    count = _i32(d, o)
    o += 4
    if not (0 <= count <= _MAX_INNER):
        raise _Bad
    children = []
    for _ in range(count):
        c_root, c_children, o = _typename(d, o, names, depth + 1)
        children.append((c_root, c_children))
    return root, children, o


def _decode_value(d: bytes, vs: int, size: int, root: str,
                  children: list, names: list[str]):
    try:
        if root == "FloatProperty" and size >= 4:
            return struct.unpack_from("<f", d, vs)[0]
        if root == "DoubleProperty" and size >= 8:
            return struct.unpack_from("<d", d, vs)[0]
        if root in ("IntProperty", "Int32Property") and size >= 4:
            return _i32(d, vs)
        if root == "BoolProperty":
            return bool(d[vs]) if size >= 1 else None
        if root == "ObjectProperty" and size >= 4:
            return f"obj:{_i32(d, vs)}"
        if root in ("NameProperty", "EnumProperty", "ByteProperty") and size >= 8:
            return _fname(d, vs, names)[0]
        if root == "StructProperty":
            # Vector/Rotator = 3 components (doubles in UE5, size 24; floats size 12)
            if size == 24:
                return tuple(struct.unpack_from("<3d", d, vs))
            if size == 12:
                return tuple(struct.unpack_from("<3f", d, vs))
    except (struct.error, _Bad, IndexError):
        return None
    return None


def _walk(d: bytes, names: list[str], start: int, end: int) -> tuple[dict, bool]:
    props: dict = {}
    p = start
    while p + 8 <= end:
        ix = _i32(d, p)
        if not (0 <= ix < len(names)):
            return props, False
        if names[ix] == "None":
            return props, True
        try:
            name, q = _fname(d, p, names)
            root, children, q = _typename(d, q, names)
            if not root.endswith("Property"):
                return props, False
            if q + 5 > end:
                return props, False
            size = _i32(d, q)
            q += 4
            flags = d[q]
            q += 1
            if flags & 0x01:
                q += 4
            if flags & 0x02:
                q += 16
            if size < 0 or q + size > end:
                return props, False
        except (_Bad, IndexError):
            return props, False
        props[name] = _decode_value(d, q, size, root, children, names)
        p = q + size
    return props, False


def property_census(index) -> "Counter":
    """Count which property names appear across all exports in a project."""
    from collections import Counter
    c: Counter = Counter()
    for pkg in index.packages.values():
        for export in pkg.exports:
            for name in decode_properties(pkg, export):
                c[name] += 1
    return c


def decode_properties(pkg: Package, export: ObjectExport) -> dict:
    """Decode an export's tagged properties into {name: value}.

    The property list is preceded by a small amount of leading data; the exact
    start is found by probing for the walk that terminates cleanly at "None".
    """
    if not pkg.source_path or "None" not in pkg.names:
        return {}
    d = Path(pkg.source_path).read_bytes()
    end = export.serial_offset + export.serial_size
    best: dict = {}
    best_score = (-1, -1)
    for start in range(export.serial_offset, export.serial_offset + _MAX_LEAD):
        props, ended = _walk(d, pkg.names, start, end)
        score = (1 if ended else 0, len(props))
        if score > best_score:
            best_score, best = score, props
    return best
