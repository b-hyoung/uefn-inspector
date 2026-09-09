"""UEFN/UE .uasset package reader (read-only, offline)."""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

UE_PACKAGE_MAGIC = 0x9E2A83C1


@dataclass
class Package:
    tag: int = 0
    legacy_file_version: int = 0
    file_version_ue4: int = 0
    file_version_ue5: int = 0
    name_count: int = 0
    name_offset: int = 0
    names: list[str] = field(default_factory=list)


def _read_fstring(data: bytes, off: int) -> tuple[str, int]:
    """Read an FString at off. Returns (value, next_off)."""
    (length,) = struct.unpack_from("<i", data, off)
    off += 4
    if length == 0:
        return "", off
    if length > 0:  # ASCII/UTF-8, length includes null terminator
        raw = data[off : off + length]
        off += length
        return raw.split(b"\x00", 1)[0].decode("utf-8", "replace"), off
    # length < 0: UTF-16LE, -length characters
    nchars = -length
    raw = data[off : off + nchars * 2]
    off += nchars * 2
    return raw.decode("utf-16-le", "replace").split("\x00", 1)[0], off


def _try_read_names(data: bytes, count: int, offset: int) -> list[str] | None:
    """Walk `count` name entries at `offset`. Each = FString + 2x uint16 hash.
    Returns names if the whole table parses cleanly, else None."""
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
        p += 4  # NonCasePreserving + CasePreserving hashes (u16 each)
        names.append(name)
    return names


def _fixed_header(data: bytes) -> tuple[int, int, int, int, int]:
    """Parse the fixed summary prefix. Returns (tag, legacy, ue4, ue5, next_off)."""
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


def read_package(path: str | Path) -> Package:
    data = Path(path).read_bytes()
    tag, legacy, ue4, ue5, after_versions = _fixed_header(data)

    # The custom-version container between the version fields and the name-table
    # pointers is variable-length; locate NameCount/NameOffset by validated scan.
    name_count = name_offset = 0
    names: list[str] = []
    for o in range(after_versions, min(len(data), 4096)):
        cand_count, cand_off = struct.unpack_from("<ii", data, o)
        parsed = _try_read_names(data, cand_count, cand_off)
        if parsed is not None and cand_count >= 5:
            name_count, name_offset, names = cand_count, cand_off, parsed
            break

    return Package(
        tag=tag,
        legacy_file_version=legacy,
        file_version_ue4=ue4,
        file_version_ue5=ue5,
        name_count=name_count,
        name_offset=name_offset,
        names=names,
    )
