"""Add a NEW @editable binding slot to a placed Verse device (size-changing).

`edit.write.set_object_ref` rewires a slot that already exists. This module
creates one that does not: it appends a name and an export modelled on an
existing `__verse_0x<hash>_<Slot>` sub-object, then fixes up every offset the
insertion moved.

⚠️ EXPERIMENTAL. Same-size patches are UEFN-verified; a *resized* package is
not. Always operate on a copy, keep the .bak, and open the result in UEFN
before trusting it.
"""
from __future__ import annotations

import shutil
import struct
from pathlib import Path

from ..core.uasset import Package, read_package

_NAME_ENTRY_TAIL = 4  # two uint16 hashes after the FString


class AddBindingError(RuntimeError):
    pass


def _fstring(text: str) -> bytes:
    raw = text.encode("utf-8") + b"\x00"
    return struct.pack("<i", len(raw)) + raw


def _name_entry(text: str) -> bytes:
    # hashes are recomputed by the engine on load; zeros are accepted by our
    # reader and by UE's non-case-preserving path.
    return _fstring(text) + b"\x00" * _NAME_ENTRY_TAIL


def _find_verse_export(pkg: Package, slot: str) -> int:
    for i, e in enumerate(pkg.exports):
        if e.object_name.startswith("__verse_") and e.object_name.endswith("_" + slot):
            return i
    raise AddBindingError(f"template slot not found: {slot}")


def _shift(value: int, cut: int, delta: int) -> int:
    """Shift an in-file offset if it sits at/after the insertion point."""
    return value + delta if value >= cut else value


def add_binding(path: str | Path, slot: str, template_slot: str,
                backup: bool = True) -> Path:
    """Wire a new @editable `slot`, copying the structure of `template_slot`.

    The new slot points at the same actor as the template until it is rewired
    with `edit.write.set_object_ref`. Returns the backup path.
    """
    p = Path(path)
    bak = p.with_suffix(p.suffix + ".bak")
    if backup:
        shutil.copy(p, bak)

    pkg = read_package(p)
    if not (pkg.export_offset and pkg.export_stride and pkg.name_offset):
        raise AddBindingError("package layout not fully parsed; refusing to edit")

    tmpl_i = _find_verse_export(pkg, template_slot)
    tmpl = pkg.exports[tmpl_i]
    new_name = tmpl.object_name.rsplit("_", 1)[0] + "_" + slot
    if new_name in pkg.names:
        raise AddBindingError(f"slot already present: {slot}")

    data = bytes(p.read_bytes())
    name_idx = pkg.name_count            # appended at the end of the name table
    export_i = pkg.export_count          # appended at the end of the export map

    # ---- 1. insert the name entry at the end of the name table -------------
    # The name table does NOT necessarily run up to import_offset (gatherable
    # text and other blocks can sit in between), so walk it to find its real end.
    name_cut = pkg.name_offset
    for _ in range(pkg.name_count):
        (ln,) = struct.unpack_from("<i", data, name_cut)
        name_cut += 4 + ln + _NAME_ENTRY_TAIL
    name_blob = _name_entry(new_name)
    d1 = data[:name_cut] + name_blob + data[name_cut:]
    dn = len(name_blob)

    # ---- 2. insert the export entry at the end of the export map -----------
    stride = pkg.export_stride
    tmpl_ent_off = pkg.export_offset + tmpl_i * stride
    entry = bytearray(data[tmpl_ent_off:tmpl_ent_off + stride])
    struct.pack_into("<i", entry, 16, name_idx)                      # ObjectName
    # serial data: clone the template's bytes, appended at end of file
    serial = data[tmpl.serial_offset:tmpl.serial_offset + tmpl.serial_size]

    export_cut = pkg.export_offset + pkg.export_count * stride + dn  # in d1 coords
    d2 = d1[:export_cut] + bytes(entry) + d1[export_cut:]
    de = stride

    out = bytearray(d2 + serial)          # new serial region goes to the very end
    new_serial_off = len(d2)

    # ---- 3. fix up every moved offset --------------------------------------
    total = dn + de

    # 3a. summary counts/pointers (positions come from the reader, not guesses)
    struct.pack_into("<i", out, pkg.name_count_pos, pkg.name_count + 1)   # NameCount
    # layout: ... | ExportCount ExportOffset ImportCount ImportOffset | trailing
    exp_cnt_pos = pkg.trailing_summary_pos - 16
    struct.pack_into("<i", out, exp_cnt_pos, pkg.export_count + 1)        # ExportCount
    struct.pack_into("<i", out, exp_cnt_pos + 4, _shift(pkg.export_offset, name_cut, dn))
    struct.pack_into("<i", out, exp_cnt_pos + 12, _shift(pkg.import_offset, name_cut, dn))
    # any other summary offset that sits after the name table also shifts
    for pos in (pkg.trailing_summary_pos - 20,):   # gatherable-text offset
        v = struct.unpack_from("<i", out, pos)[0]
        if 0 < v <= len(data):
            struct.pack_into("<i", out, pos, _shift(v, name_cut, dn))

    # 3b. trailing summary offsets (depends map, asset registry, bulk data, ...)
    from .rebuild import trailing_offsets
    for pos, value in trailing_offsets(data, pkg):
        v = _shift(value, name_cut, dn)
        v = _shift(v, export_cut, de)
        if v != value:
            struct.pack_into("<i", out, pos, v)

    # 3c. every export's serial offset (data moved by dn + de)
    new_export_off = _shift(pkg.export_offset, name_cut, dn)
    for k in range(pkg.export_count):
        ent = new_export_off + k * stride
        off = struct.unpack_from("<q", out, ent + 36)[0]
        struct.pack_into("<q", out, ent + 36, off + total)

    # 3d. the new export's own serial pointer
    new_ent = new_export_off + pkg.export_count * stride
    struct.pack_into("<q", out, new_ent + 28, len(serial))        # SerialSize
    struct.pack_into("<q", out, new_ent + 36, new_serial_off)     # SerialOffset

    p.write_bytes(bytes(out))

    # ---- 4. validate; roll back if we broke it -----------------------------
    check = read_package(p)
    ok = (check.export_count == pkg.export_count + 1
          and new_name in check.names
          and all(0 < e.serial_offset and e.serial_offset + e.serial_size <= len(out)
                  for e in check.exports))
    if not ok:
        if backup:
            shutil.copy(bak, p)
        raise AddBindingError("resize produced an inconsistent package — rolled back")
    return bak
