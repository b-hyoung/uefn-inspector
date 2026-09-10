"""Add an IMPORT entry (cross-package object reference) to a package.

`edit.write.set_object_ref` can only repoint a slot at a package index that
already exists. Wiring an @editable slot to an actor that lives in ANOTHER
OFPA package therefore needs new imports first: this module appends one
FObjectImport row (and any name-table entries it needs) and fixes up every
offset the insertion moved — the same fixup discipline as `add_binding.py`.

Serialized form (ground truth: a file UEFN wrote after binding slots in-editor):

    ClassPackage FName | ClassName FName | OuterIndex int32 |
    ObjectName FName   | PackageName FName | bImportOptional int32   (= 40 bytes)

Numbered FNames follow UE's own rule: "foo_0" is FName("foo", Number=1), so a
trailing "_<digits>" is split off `object_name` and stored in the Number field.

The new row goes at the END of the import map so no existing FPackageIndex
(export map, depends map, preload deps, property values) changes meaning.

⚠️ EXPERIMENTAL. Structure round-trips through our reader; UEFN acceptance of
a resized package is not verified. Operate on a copy and keep the .bak.
"""
from __future__ import annotations

import shutil
import struct
from pathlib import Path

from ..core.uasset import ObjectImport, Package, read_package
from .add_binding import _name_entry, _shift
from .rebuild import trailing_offsets

_NAME_ENTRY_TAIL = 4


class AddImportError(RuntimeError):
    pass


def split_fname(text: str) -> tuple[str, int]:
    """UE FName construction rule: "name_<N>" -> ("name", N + 1); else (text, 0).

    The digits must be a canonical decimal (no leading zero unless "0") and fit
    the Number field; anything else is kept verbatim as part of the name.
    """
    base, sep, tail = text.rpartition("_")
    if (sep and base and tail.isdigit() and tail.isascii() and len(tail) <= 10
            and (tail == "0" or not tail.startswith("0"))
            and int(tail) < 0x7FFFFFFF):
        return base, int(tail) + 1
    return text, 0


def find_import(pkg: Package, *, class_package: str, class_name: str,
                outer_index: int, object_name: str, package_name: str = "") -> int:
    """Return the (negative) index of an identical existing import, or 0."""
    base, number = split_fname(object_name)
    for k, imp in enumerate(pkg.imports):
        if (imp.class_package == class_package and imp.class_name == class_name
                and imp.outer_index == outer_index and imp.object_name == base
                and imp.object_number == number
                and imp.package_name == package_name):
            return -(k + 1)
    return 0


def _name_table_end(data: bytes, pkg: Package) -> int:
    cut = pkg.name_offset
    for _ in range(pkg.name_count):
        (ln,) = struct.unpack_from("<i", data, cut)
        cut += 4 + ln + _NAME_ENTRY_TAIL
    return cut


def _grow_tables(data: bytes, pkg: Package, new_names: list[str],
                 row: bytes = b"") -> bytearray:
    """Append `new_names` to the name table and `row` (one import, may be
    empty) to the import map, fixing up every offset the insertions move."""
    names = list(pkg.names) + new_names
    name_cut = _name_table_end(data, pkg)
    name_blob = b"".join(_name_entry(w) for w in new_names)
    d1 = data[:name_cut] + name_blob + data[name_cut:]
    dn = len(name_blob)
    stride = pkg.import_stride
    import_cut = _shift(pkg.import_offset + pkg.import_count * stride, name_cut, dn)
    out = bytearray(d1[:import_cut] + row + d1[import_cut:])
    di = len(row)
    new_imports = pkg.import_count + (1 if row else 0)

    def moved(v: int) -> int:
        """An original-file offset after both insertions."""
        return _shift(_shift(v, name_cut, dn), import_cut, di)

    # ---- fix up every moved offset (same summary positions as add_binding)
    struct.pack_into("<i", out, pkg.name_count_pos, len(names))              # NameCount
    exp_cnt_pos = pkg.trailing_summary_pos - 16
    # layout: ... | ExportCount ExportOffset ImportCount ImportOffset | trailing
    struct.pack_into("<i", out, exp_cnt_pos + 4, moved(pkg.export_offset))   # ExportOffset
    struct.pack_into("<i", out, exp_cnt_pos + 8, new_imports)                # ImportCount
    struct.pack_into("<i", out, exp_cnt_pos + 12, moved(pkg.import_offset))  # ImportOffset
    # other summary offsets that can sit after the name table:
    #   gatherable-text offset (trailing-20) and SoftObjectPaths offset
    #   (NameCount+12) — both point at the name table's end in UEFN files.
    for pos in (pkg.trailing_summary_pos - 20, pkg.name_count_pos + 12):
        v = struct.unpack_from("<i", out, pos)[0]
        if 0 < v <= len(data):
            struct.pack_into("<i", out, pos, moved(v))
    # trailing summary offsets (depends map, asset registry, bulk data, ...)
    for pos, value in trailing_offsets(data, pkg):
        v = moved(value)
        if v != value:
            struct.pack_into("<i", out, pos, v)
    # every export's serial offset (all sit after the import map)
    new_export_off = moved(pkg.export_offset)
    for k in range(pkg.export_count):
        ent = new_export_off + k * pkg.export_stride
        off = struct.unpack_from("<q", out, ent + 36)[0]
        struct.pack_into("<q", out, ent + 36, moved(off))
    return out


def _check_layout(pkg: Package) -> None:
    if not (pkg.export_offset and pkg.export_stride and pkg.name_offset
            and pkg.import_offset and pkg.import_stride):
        raise AddImportError("package layout not fully parsed; refusing to edit")


def _consistent(check: Package, before: Package, size: int) -> bool:
    return (check.names[:before.name_count] == before.names
            and check.imports[:before.import_count] == before.imports
            and check.export_count == before.export_count
            and [e.object_name for e in check.exports] == [e.object_name for e in before.exports]
            and all(0 < e.serial_offset and e.serial_offset + e.serial_size <= size
                    for e in check.exports))


def ensure_names(path: str | Path, words: list[str], backup: bool = True) -> list[int]:
    """Make sure every word is in the name table (appending the missing ones);
    return their name indices. The file is untouched when nothing is missing."""
    p = Path(path)
    pkg = read_package(p)
    missing = []
    for w in words:
        if w not in pkg.names and w not in missing:
            missing.append(w)
    if missing:
        _check_layout(pkg)
        bak = p.with_suffix(p.suffix + ".bak")
        if backup:
            shutil.copy(p, bak)
        out = _grow_tables(bytes(p.read_bytes()), pkg, missing)
        p.write_bytes(bytes(out))
        check = read_package(p)
        if not (check.name_count == pkg.name_count + len(missing)
                and _consistent(check, pkg, len(out))):
            if backup:
                shutil.copy(bak, p)
            raise AddImportError("resize produced an inconsistent package — rolled back")
        pkg = check
    return [pkg.names.index(w) for w in words]


def add_import(path: str | Path, *, class_package: str, class_name: str,
               outer_index: int, object_name: str, package_name: str = "",
               backup: bool = True) -> int:
    """Append an import row; return its FPackageIndex (negative).

    Idempotent: if an identical row already exists its index is returned and
    the file is left untouched. `outer_index` must be 0 or an existing import.
    """
    p = Path(path)
    pkg = read_package(p)
    _check_layout(pkg)
    if not (-pkg.import_count <= outer_index <= 0):
        raise AddImportError(f"outer index {outer_index} is not an existing import")

    existing = find_import(pkg, class_package=class_package, class_name=class_name,
                           outer_index=outer_index, object_name=object_name,
                           package_name=package_name)
    if existing:
        return existing

    bak = p.with_suffix(p.suffix + ".bak")
    if backup:
        shutil.copy(p, bak)

    data = bytes(p.read_bytes())
    stride = pkg.import_stride
    obj_base, obj_number = split_fname(object_name)

    # ---- 1. name-table entries (reuse existing, append the rest) ------------
    names = list(pkg.names)
    new_names: list[str] = []
    for w in (class_package, class_name, obj_base, package_name or "None"):
        if w not in names and w not in new_names:
            new_names.append(w)
    names += new_names

    # ---- 2. the import row, appended at the end of the import map ----------
    row = bytearray(stride)
    struct.pack_into("<ii", row, 0, names.index(class_package), 0)
    struct.pack_into("<ii", row, 8, names.index(class_name), 0)
    struct.pack_into("<i", row, 16, outer_index)
    struct.pack_into("<ii", row, 20, names.index(obj_base), obj_number)
    if stride >= 36:
        struct.pack_into("<ii", row, 28, names.index(package_name or "None"), 0)
    if stride >= 40:
        struct.pack_into("<i", row, 36, 0)                         # bImportOptional

    # ---- 3. splice both in and fix up every moved offset ------------------
    out = _grow_tables(data, pkg, new_names, bytes(row))
    p.write_bytes(bytes(out))

    # ---- 4. validate; roll back if we broke it -----------------------------
    new_index = -(pkg.import_count + 1)
    check = read_package(p)
    expect = ObjectImport(class_package=class_package, class_name=class_name,
                          object_name=obj_base, outer_index=outer_index,
                          package_name=package_name if stride >= 36 else "",
                          object_number=obj_number)
    ok = (check.import_count == pkg.import_count + 1
          and check.name_count == len(names)
          and check.imports[-1] == expect
          and _consistent(check, pkg, len(out)))
    if not ok:
        if backup:
            shutil.copy(bak, p)
        raise AddImportError("resize produced an inconsistent package — rolled back")
    return new_index
