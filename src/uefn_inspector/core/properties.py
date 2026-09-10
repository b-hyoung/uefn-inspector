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

from uefn_inspector.core.uasset import ObjectExport, Package, _read_fstring

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


_TAGFLAG_BOOL_TRUE = 0x10


def _decode_value(d: bytes, vs: int, size: int, root: str,
                  children: list, names: list[str], flags: int = 0):
    try:
        if root == "FloatProperty" and size >= 4:
            return struct.unpack_from("<f", d, vs)[0]
        if root == "DoubleProperty" and size >= 8:
            return struct.unpack_from("<d", d, vs)[0]
        if root in ("IntProperty", "Int32Property", "UInt32Property") and size >= 4:
            return _i32(d, vs)
        if root == "BoolProperty":
            # UE5.4: the bool value lives in the PropertyTagFlags (BoolTrue bit),
            # not the value region (which is empty, size 0).
            return bool(flags & _TAGFLAG_BOOL_TRUE)
        if root == "StrProperty" and size >= 4:
            return _read_fstring(d, vs)[0]
        if root == "ArrayProperty" and size >= 4:
            inner = children[0][0] if children else ""
            count = _i32(d, vs)
            if inner == "ObjectProperty" and 0 <= count <= (size - 4) // 4:
                return [_i32(d, vs + 4 + 4 * i) for i in range(count)]
            return {"count": count, "inner": inner}  # partial: element decode TBD
        if root == "SoftObjectProperty" and size >= 4:
            return _read_fstring(d, vs)[0]
        if root == "ObjectProperty" and size >= 4:
            return f"obj:{_i32(d, vs)}"
        if root in ("NameProperty", "EnumProperty", "ByteProperty") and size >= 8:
            return _fname(d, vs, names)[0]
        if root == "StructProperty":
            sname = children[0][0] if children else ""
            if sname in ("Vector", "Rotator", "Vector_NetQuantize") and size == 24:
                return tuple(struct.unpack_from("<3d", d, vs))
            if sname in ("Vector", "Rotator") and size == 12:
                return tuple(struct.unpack_from("<3f", d, vs))
            if sname == "Vector2D" and size == 16:
                return tuple(struct.unpack_from("<2d", d, vs))
            if sname == "LinearColor" and size == 16:
                return tuple(struct.unpack_from("<4f", d, vs))
            if sname == "Quat" and size == 32:
                return tuple(struct.unpack_from("<4d", d, vs))
            if sname == "Guid" and size == 16:
                return d[vs:vs + 16].hex()
            if sname == "IntPoint" and size == 8:
                return tuple(struct.unpack_from("<2i", d, vs))
            # unnamed/other: fall back to the common 3-component shape
            if size == 24:
                return tuple(struct.unpack_from("<3d", d, vs))
            if size == 12:
                return tuple(struct.unpack_from("<3f", d, vs))
    except (struct.error, _Bad, IndexError):
        return None
    return None


def _walk(d: bytes, names: list[str], start: int, end: int) -> tuple[dict, bool, dict, dict, int]:
    """Returns (values, ended_at_None, layout, spans, stop) where
    layout = {name: (value_offset, size, type_root)}  — enables in-place writes,
    spans  = {name: (tag_offset, tag_end)}            — whole FPropertyTag incl. value,
    stop   = offset where the walk stopped (the "None" tag when ended_at_None)."""
    props: dict = {}
    layout: dict = {}
    spans: dict = {}
    p = start
    while p + 8 <= end:
        ix = _i32(d, p)
        if not (0 <= ix < len(names)):
            return props, False, layout, spans, p
        if names[ix] == "None":
            return props, True, layout, spans, p
        try:
            name, q = _fname(d, p, names)
            root, children, q = _typename(d, q, names)
            if not root.endswith("Property"):
                return props, False, layout, spans, p
            if q + 5 > end:
                return props, False, layout, spans, p
            size = _i32(d, q)
            q += 4
            flags = d[q]
            q += 1
            if flags & 0x01:
                q += 4
            if flags & 0x02:
                q += 16
            if size < 0 or q + size > end:
                return props, False, layout, spans, p
        except (_Bad, IndexError):
            return props, False, layout, spans, p
        props[name] = _decode_value(d, q, size, root, children, names, flags)
        layout[name] = (q, size, root)
        spans[name] = (p, q + size)
        p = q + size
    return props, False, layout, spans, p


def _best_walk(d: bytes, names: list[str], export) -> tuple[dict, dict, dict, int | None]:
    """Probe leading offsets, return (values, layout, spans, terminator) of the
    cleanest walk; `terminator` is the file offset of the closing "None" tag,
    or None when no probe terminated cleanly."""
    end = export.serial_offset + export.serial_size
    best_score = (-1, -1)
    best: tuple[dict, dict, dict, int | None] = ({}, {}, {}, None)
    for start in range(export.serial_offset, export.serial_offset + _MAX_LEAD):
        vals, ended, layout, spans, stop = _walk(d, names, start, end)
        score = (1 if ended else 0, len(vals))
        if score > best_score:
            best_score, best = score, (vals, layout, spans, stop if ended else None)
    return best


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
    return _best_walk(d, pkg.names, export)[0]


def property_layout(pkg: Package, export: ObjectExport) -> dict:
    """{name: (value_offset, size, type_root)} — for in-place writes."""
    if not pkg.source_path or "None" not in pkg.names:
        return {}
    d = Path(pkg.source_path).read_bytes()
    return _best_walk(d, pkg.names, export)[1]


def property_spans(pkg: Package, export: ObjectExport) -> dict:
    """{name: (tag_offset, tag_end)} — the whole serialized FPropertyTag
    (name, type name, size, flags, value) of each property; for cloning tags."""
    if not pkg.source_path or "None" not in pkg.names:
        return {}
    d = Path(pkg.source_path).read_bytes()
    return _best_walk(d, pkg.names, export)[2]


def property_terminator(pkg: Package, export: ObjectExport) -> int | None:
    """File offset of the "None" tag that closes the export's property list
    (where a new tag must be inserted), or None if the list does not parse."""
    if not pkg.source_path or "None" not in pkg.names:
        return None
    d = Path(pkg.source_path).read_bytes()
    return _best_walk(d, pkg.names, export)[3]
