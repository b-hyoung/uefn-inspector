"""UEFN/UE .uasset package reader (read-only, offline).

Produces a faithful, byte-addressable model (names + imports + exports with
serial regions) so analysis (A) and a future writer (B) share one model.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

UE_PACKAGE_MAGIC = 0x9E2A83C1


@dataclass
class ObjectImport:
    """One FObjectImport row (UE5 stride 40):

        ClassPackage FName(8) | ClassName FName(8) | OuterIndex int32 |
        ObjectName FName(8)   | PackageName FName(8) | bImportOptional int32

    `object_name` is the FName *base* string as stored in the name table; the
    FName Number (0 = none) is kept in `object_number` and rendered by
    `full_name` the way UE does: Number=1 -> "<name>_0".
    """
    class_package: str = ""
    class_name: str = ""
    object_name: str = ""
    outer_index: int = 0       # FPackageIndex of the outer (0 = none / package root)
    package_name: str = ""     # OFPA/external package the object lives in ("" = None)
    optional: bool = False     # bImportOptional
    object_number: int = 0     # raw FName Number of ObjectName (0 = unnumbered)

    @property
    def full_name(self) -> str:
        return (f"{self.object_name}_{self.object_number - 1}"
                if self.object_number > 0 else self.object_name)


@dataclass
class ObjectExport:
    object_name: str = ""
    class_index: int = 0
    super_index: int = 0
    outer_index: int = 0
    serial_offset: int = 0
    serial_size: int = 0


@dataclass
class Package:
    tag: int = 0
    legacy_file_version: int = 0
    file_version_ue4: int = 0
    file_version_ue5: int = 0
    name_count: int = 0
    name_offset: int = 0
    names: list[str] = field(default_factory=list)
    import_count: int = 0
    import_stride: int = 0
    imports: list[ObjectImport] = field(default_factory=list)
    export_count: int = 0
    exports: list[ObjectExport] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_path: str = ""
    # layout info for the rebuild/fixup engine
    export_offset: int = 0
    export_stride: int = 0
    import_offset: int = 0
    trailing_summary_pos: int = 0  # first byte after ImportOffset field
    name_count_pos: int = 0        # position of the NameCount summary field


def _i32(data: bytes, o: int) -> int:
    return struct.unpack_from("<i", data, o)[0]


def _i64(data: bytes, o: int) -> int:
    return struct.unpack_from("<q", data, o)[0]


def _read_fstring(data: bytes, off: int) -> tuple[str, int]:
    (length,) = struct.unpack_from("<i", data, off)
    off += 4
    if length == 0:
        return "", off
    if length > 0:  # ASCII/UTF-8, length includes null terminator
        raw = data[off : off + length]
        off += length
        return raw.split(b"\x00", 1)[0].decode("utf-8", "replace"), off
    nchars = -length
    raw = data[off : off + nchars * 2]
    off += nchars * 2
    return raw.decode("utf-16-le", "replace").split("\x00", 1)[0], off


def _read_fname(data: bytes, off: int, names: list[str]) -> str:
    idx = _i32(data, off)
    return names[idx] if 0 <= idx < len(names) else f"?{idx}"


def _try_read_names(data: bytes, count: int, offset: int) -> list[str] | None:
    """Walk `count` name entries at `offset`. Each = FString + 2x uint16 hash."""
    n = len(data)
    if not (1 <= count <= 1_000_000) or not (0 < offset < n):
        return None
    names: list[str] = []
    p = offset
    for _ in range(count):
        if p + 4 > n:
            return None
        (length,) = struct.unpack_from("<i", data, p)
        if length <= 0 or p + 4 + length + 4 > n:
            return None
        name, p = _read_fstring(data, p)
        p += 4  # NonCasePreserving + CasePreserving hashes
        names.append(name)
    return names


def _fixed_header(data: bytes) -> tuple[int, int, int, int, int]:
    tag, legacy = struct.unpack_from("<Ii", data, 0)
    off = 8 + 4  # skip legacy_ue3_version
    (ue4,) = struct.unpack_from("<i", data, off)
    off += 4
    ue5 = 0
    if legacy <= -8:
        (ue5,) = struct.unpack_from("<i", data, off)
        off += 4
    off += 4  # file_version_licensee_ue4
    return tag, legacy, ue4, ue5, off


def _find_name_anchor(data: bytes, start: int) -> tuple[int, int, int, list[str]] | None:
    """Locate the (NameCount, NameOffset) summary field pair by validated scan.
    Returns (field_pos, count, offset, names)."""
    for o in range(start, max(start, min(len(data) - 8, 4096))):
        cand_count, cand_off = struct.unpack_from("<ii", data, o)
        parsed = _try_read_names(data, cand_count, cand_off)
        if parsed is not None and cand_count >= 5:
            return o, cand_count, cand_off, parsed
    return None


def _import_stride(offset: int, count: int, export_offset: int) -> int:
    """Import stride is fixed per package; derive it from the gap to the next
    table when exports follow imports, else fall back to the known 40."""
    if count > 0 and export_offset > offset:
        gap = export_offset - offset
        if gap % count == 0 and 28 <= gap // count <= 64:
            return gap // count
    return 40


def _parse_imports(data: bytes, offset: int, count: int, stride: int,
                   names: list[str]) -> list[ObjectImport]:
    n = len(data)
    imports: list[ObjectImport] = []
    for k in range(count):
        o = offset + k * stride
        if o + 28 > n:
            break
        imp = ObjectImport(
            class_package=_read_fname(data, o, names),
            class_name=_read_fname(data, o + 8, names),
            outer_index=_i32(data, o + 16),
            object_name=_read_fname(data, o + 20, names),
            object_number=_i32(data, o + 24),
        )
        # stride-aware tail: PackageName (FName) and bImportOptional (int32)
        # only exist on newer packages (UE5: 40 bytes).
        if stride >= 36 and o + 36 <= n:
            pn = _read_fname(data, o + 28, names)
            imp.package_name = "" if pn == "None" else pn
        if stride >= 40 and o + 40 <= n:
            imp.optional = bool(_i32(data, o + 36))
        imports.append(imp)
    return imports


def _detect_export_stride(data: bytes, offset: int, count: int,
                          names: list[str]) -> int | None:
    n = len(data)
    for stride in [112] + list(range(72, 144, 4)):
        offs = []
        ok = True
        for k in range(count):
            o = offset + k * stride
            if o + 44 > n:
                ok = False
                break
            name_idx = _i32(data, o + 16)
            size = _i64(data, o + 28)
            soff = _i64(data, o + 36)
            if not (0 <= name_idx < len(names) and 0 < soff < n
                    and 0 < size < n and soff + size <= n):
                ok = False
                break
            offs.append(soff)
        if ok and offs == sorted(offs):
            return stride
    return None


def _parse_exports(data: bytes, offset: int, count: int,
                   names: list[str]) -> list[ObjectExport]:
    stride = _detect_export_stride(data, offset, count, names)
    if stride is None:
        return []
    exports: list[ObjectExport] = []
    for k in range(count):
        o = offset + k * stride
        exports.append(ObjectExport(
            object_name=_read_fname(data, o + 16, names),
            class_index=_i32(data, o),
            super_index=_i32(data, o + 4),
            outer_index=_i32(data, o + 12),
            serial_size=_i64(data, o + 28),
            serial_offset=_i64(data, o + 36),
        ))
    return exports


def read_package(path: str | Path) -> Package:
    data = Path(path).read_bytes()
    pkg = Package(source_path=str(path))
    if len(data) < 24:
        pkg.warnings.append("file too short for package header")
        return pkg
    try:
        tag, legacy, ue4, ue5, after_versions = _fixed_header(data)
    except struct.error:
        pkg.warnings.append("header parse failed")
        return pkg
    pkg.tag, pkg.legacy_file_version = tag, legacy
    pkg.file_version_ue4, pkg.file_version_ue5 = ue4, ue5

    anchor = _find_name_anchor(data, after_versions)
    if anchor is None:
        pkg.warnings.append("name table not found")
        return pkg
    o, pkg.name_count, pkg.name_offset, pkg.names = anchor
    pkg.name_count_pos = o

    # Walk the summary forward from the NameCount field through the known
    # post-name layout to reach the export/import table pointers.
    try:
        p = o + 8          # skip NameCount, NameOffset
        p += 8             # SoftObjectPaths count/offset
        _, p = _read_fstring(data, p)   # LocalizationId
        p += 8             # GatherableTextData count/offset
        export_count, export_offset = struct.unpack_from("<ii", data, p)
        p += 8
        import_count, import_offset = struct.unpack_from("<ii", data, p)
        p += 8
    except struct.error:
        pkg.warnings.append("summary walk failed")
        return pkg

    pkg.import_offset = import_offset
    pkg.trailing_summary_pos = p  # first byte after ImportOffset field

    n = len(data)
    if 0 < import_offset < n and 0 <= import_count < 100000:
        pkg.import_count = import_count
        pkg.import_stride = _import_stride(import_offset, import_count, export_offset)
        pkg.imports = _parse_imports(data, import_offset, import_count,
                                     pkg.import_stride, pkg.names)
    if 0 < export_offset < n and 0 <= export_count < 100000:
        pkg.export_count = export_count
        pkg.export_offset = export_offset
        pkg.export_stride = _detect_export_stride(data, export_offset,
                                                  export_count, pkg.names) or 0
        pkg.exports = _parse_exports(data, export_offset, export_count, pkg.names)

    return pkg
