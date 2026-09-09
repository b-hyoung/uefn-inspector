"""Size-changing package edits (offset-fixup engine).

Splices new bytes into an export's serial region and fixes up moved offsets.
Built incrementally & test-first.

STATUS / SCOPE (honest):
  * Same-size replacement: pure splice. Fully safe.
  * Different-size: fixes the EXPORT MAP (each export's SerialSize/SerialOffset).
    Our own parser reads the result correctly (names/imports/export-map/export-
    data all resolve). This is verified by tests.
  * NOT yet handled: trailing summary offsets (DependsOffset, BulkDataStartOffset,
    AssetRegistryDataOffset, ...) that UE uses at load time. Until those are
    fixed too, UEFN ACCEPTANCE of a resized package is NOT guaranteed. That is
    the risky remaining step.
"""
from __future__ import annotations

import struct

from .uasset import Package


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

    # Fix the export map: this export's size, and every later export's offset.
    eo, stride = pkg.export_offset, pkg.export_stride
    for k in range(pkg.export_count):
        ent = eo + k * stride
        serial_off = struct.unpack_from("<q", out, ent + 36)[0]
        if serial_off == start:
            struct.pack_into("<q", out, ent + 28, len(new_serial_bytes))  # SerialSize
        elif serial_off > start:
            struct.pack_into("<q", out, ent + 36, serial_off + delta)     # SerialOffset
    return out
