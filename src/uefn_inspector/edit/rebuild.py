"""Size-changing package edits (offset-fixup engine).

Splices new bytes into an export's serial region and fixes up every offset that
moves:

  * the export map     — SerialSize of the edited export, SerialOffset of later ones
  * the trailing summary offsets — depends map, asset-registry, bulk-data start …
    (any summary offset pointing at/after the edit shifts by the same delta)

Offsets that live *before* the edited region are left untouched.

STATUS (honest): our own parser round-trips the result, and the offsets are
provably consistent (see tests). UEFN acceptance of a *resized* package is NOT
yet verified — same-size patches are (see edit/write.py). Treat resizing as
experimental and always work on a copy.
"""
from __future__ import annotations

import struct

from ..core.uasset import Package

# Summary layout: right after the ImportOffset field comes a run of int32
# offsets (DependsOffset, SoftPackageReferences, SearcherName, Thumbnail,
# AssetRegistryData, BulkDataStartOffset, …). Their exact order varies by
# version, so we discover them by shape instead of hard-coding indices.
_MAX_TRAILING_FIELDS = 16


def trailing_offsets(data: bytes, pkg: Package) -> list[tuple[int, int]]:
    """[(field_position, offset_value)] for summary offsets after ImportOffset.

    Only plausible in-file offsets are reported: 0 < value <= filesize, and the
    field itself sits between the trailing summary start and the name table.
    """
    out: list[tuple[int, int]] = []
    n = len(data)
    start = pkg.trailing_summary_pos
    if not start or not pkg.name_offset:
        return out
    for k in range(_MAX_TRAILING_FIELDS):
        pos = start + k * 4
        if pos + 4 > n or pos >= pkg.name_offset:
            break
        (value,) = struct.unpack_from("<i", data, pos)
        if 0 < value <= n:
            out.append((pos, value))
    return out


def resize_export_data(data: bytes, pkg: Package, export_index: int,
                       new_serial_bytes: bytes) -> bytearray:
    """Replace export[export_index]'s serial data. Returns a new bytearray."""
    e = pkg.exports[export_index]
    start, size = e.serial_offset, e.serial_size
    delta = len(new_serial_bytes) - size

    out = bytearray(data[:start]) + bytearray(new_serial_bytes) + bytearray(data[start + size:])
    if delta == 0:
        return out

    if not (pkg.export_offset and pkg.export_stride):
        raise RuntimeError("export map layout unknown; cannot fix up offsets")

    # 1) export map: this export's size, and every later export's offset
    eo, stride = pkg.export_offset, pkg.export_stride
    for k in range(pkg.export_count):
        ent = eo + k * stride
        serial_off = struct.unpack_from("<q", out, ent + 36)[0]
        if serial_off == start:
            struct.pack_into("<q", out, ent + 28, len(new_serial_bytes))  # SerialSize
        elif serial_off > start:
            struct.pack_into("<q", out, ent + 36, serial_off + delta)     # SerialOffset

    # 2) trailing summary offsets that point at/after the edited region
    for pos, value in trailing_offsets(data, pkg):
        if value > start:
            struct.pack_into("<i", out, pos, value + delta)

    return out
