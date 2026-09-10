"""Hand-built minimal .uasset packages for fixture-free structural tests.

Produces the smallest layout our reader accepts: fixed header, summary
(NameCount .. ImportOffset + three trailing offsets), name table, 40-byte
import rows, 112-byte export rows, serial data, depends map. Values that the
reader does not interpret are zero.
"""
from __future__ import annotations

import struct

from uefn_inspector.core.uasset import UE_PACKAGE_MAGIC

IMPORT_STRIDE = 40
EXPORT_STRIDE = 112


def name_entry(text: str) -> bytes:
    raw = text.encode("utf-8") + b"\x00"
    return struct.pack("<i", len(raw)) + raw + b"\x00" * 4


def fname(names: list[str], text: str, number: int = 0) -> bytes:
    return struct.pack("<ii", names.index(text), number)


def object_props(names: list[str], props: dict[str, int]) -> bytes:
    """An export's serial data as UEFN writes it for a Verse sub-object:
    leading 0 byte, tagged ObjectProperties {prop_name: FPackageIndex},
    the "None" terminator, then a 4-byte zero tail."""
    out = b"\x00"
    for prop, value in props.items():
        out += fname(names, prop) + fname(names, "ObjectProperty") + struct.pack("<i", 0)
        out += struct.pack("<iBi", 4, 0, value)
    return out + fname(names, "None") + b"\x00" * 4


def build_package(names: list[str], imports: list[tuple], exports: list[tuple]) -> bytes:
    """imports: (class_package, class_name, outer_index, object_name, number, package_name)
    exports: (object_name, class_index, outer_index, serial_bytes)"""
    header = struct.pack("<IiiiiI", UE_PACKAGE_MAGIC, -8, 0, 522, 1018, 0)
    summary_len = 10 * 4 + 4 + 3 * 4          # 10 int fields, empty LocalizationId FString, 3 trailing
    name_off = len(header) + summary_len
    name_blob = b"".join(name_entry(n) for n in names)
    import_off = name_off + len(name_blob)
    export_off = import_off + IMPORT_STRIDE * len(imports)
    serial_off = export_off + EXPORT_STRIDE * len(exports)

    rows = b""
    for cp, cn, outer, on, num, pn in imports:
        rows += fname(names, cp) + fname(names, cn) + struct.pack("<i", outer)
        rows += fname(names, on, num) + fname(names, pn or "None") + struct.pack("<i", 0)

    ex_rows, serial, cur = b"", b"", serial_off
    for on, cls, outer, blob in exports:
        row = bytearray(EXPORT_STRIDE)
        struct.pack_into("<iii", row, 0, cls, 0, 0)
        struct.pack_into("<i", row, 12, outer)
        row[16:24] = fname(names, on)
        struct.pack_into("<qq", row, 28, len(blob), cur)
        ex_rows += bytes(row)
        serial += blob
        cur += len(blob)
    depends_off = cur
    depends = struct.pack("<i", 0) * len(exports)
    total = depends_off + len(depends)

    summary = struct.pack("<ii", len(names), name_off)
    summary += struct.pack("<ii", 0, import_off)            # SoftObjectPaths (count, offset)
    summary += struct.pack("<i", 0)                         # LocalizationId ""
    summary += struct.pack("<ii", 0, import_off)            # GatherableText (count, offset)
    summary += struct.pack("<iiii", len(exports), export_off, len(imports), import_off)
    summary += struct.pack("<iii", depends_off, 0, total)   # trailing: depends, -, bulk start
    assert len(summary) == summary_len
    return header + summary + name_blob + rows + ex_rows + serial + depends


# A placed Verse device in the shape UEFN writes for stock-device slots:
# PersistentLevel chain, the device export whose `__verse_0x<hash>_<Slot>`
# ObjectProperties point at SUB-OBJECT EXPORTS of the same name, and the
# binding itself as a `SavedActor` ObjectProperty on that sub-object.
LIGHT_PKG = "/MyProject/__ExternalActors__/MyProject/0/EC/LIGHTPKG"
LIGHT_ACTOR = "Device_PointLight_V2_C_UAID_AAAA000000000000_1"
DEVICE_NAMES = [
    "/Script/CoreUObject", "/Script/Engine", "/MyProject/_Verse", "/MyProject/MyProject",
    "Package", "World", "Level", "VerseClass", "MyProject", "PersistentLevel",
    "my_gate", "Other", "None", "ObjectProperty",
    "__verse_0x0000000A_Light", "__verse_0x0000000B_Trigger",
    "/CRD_PointLight/Device_PointLight_V2", "Device_PointLight_V2_C", LIGHT_PKG,
    "Device_PointLight_V2_C_UAID_AAAA000000000000",
]
DEVICE_IMPORTS = [
    ("/Script/CoreUObject", "Package", 0, "/MyProject/MyProject", 0, ""),   # -1
    ("/Script/Engine", "World", -1, "MyProject", 0, ""),                    # -2
    ("/Script/Engine", "Level", -2, "PersistentLevel", 0, ""),              # -3
    ("/Script/CoreUObject", "Package", 0, "/MyProject/_Verse", 0, ""),      # -4
    ("/Script/CoreUObject", "VerseClass", -4, "my_gate", 0, ""),            # -5
    ("/Script/CoreUObject", "Package", 0, LIGHT_PKG, 0, ""),                # -6
    ("/CRD_PointLight/Device_PointLight_V2", "Device_PointLight_V2_C", -3,
     "Device_PointLight_V2_C_UAID_AAAA000000000000", 2, LIGHT_PKG),         # -7 (bound actor)
]
LIGHT_ACTOR_INDEX = -7


def device_package(bound_light: bool = True) -> bytes:
    """Two slots: `Light` (bound to import -7 via SavedActor when `bound_light`,
    else a fresh placeholder) and `Trigger` (always a fresh placeholder). With
    `bound_light=False` the name table has no "SavedActor" at all."""
    names = DEVICE_NAMES + (["SavedActor"] if bound_light else [])
    slots = object_props(names, {"__verse_0x0000000A_Light": 2,
                                 "__verse_0x0000000B_Trigger": 3})
    light = object_props(names, {"SavedActor": LIGHT_ACTOR_INDEX} if bound_light else {})
    exports = [("my_gate", -5, 0, slots),
               ("__verse_0x0000000A_Light", -5, 1, light),
               ("__verse_0x0000000B_Trigger", -5, 1, object_props(names, {})),
               ("Other", -5, 0, object_props(names, {}))]
    return build_package(names, DEVICE_IMPORTS, exports)


def wrapper_form_package() -> bytes:
    """The (wrong for stock devices) legacy form: the slot property points at
    an import instead of a sub-object export."""
    slots = object_props(DEVICE_NAMES, {"__verse_0x0000000A_Light": -7,
                                        "__verse_0x0000000B_Trigger": 3})
    exports = [("my_gate", -5, 0, slots),
               ("__verse_0x0000000B_Trigger", -5, 1, object_props(DEVICE_NAMES, {}))]
    return build_package(DEVICE_NAMES, DEVICE_IMPORTS, exports)
