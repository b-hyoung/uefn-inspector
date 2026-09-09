"""Verse device @editable binding extraction (offline).

The bindings the editor GUI wires (and that runtime reflection could NOT read)
are serialized on disk as `__verse_0x<hash>_<Slot>` sub-object exports whose
`SavedActor` object-property points at the bound actor. This reads them.
"""
from __future__ import annotations

import re

from .properties import decode_properties
from .uasset import Package

_SLOT = re.compile(r"__verse_0x[0-9A-Fa-f]+_(.+)")


def resolve_ref(pkg: Package, ref) -> str | None:
    """Resolve an ObjectProperty value ("obj:N" / FPackageIndex) to a name."""
    if isinstance(ref, str) and ref.startswith("obj:"):
        ref = int(ref[4:])
    if not isinstance(ref, int) or ref == 0:
        return None
    if ref > 0 and ref - 1 < len(pkg.exports):
        return pkg.exports[ref - 1].object_name
    if ref < 0 and -ref - 1 < len(pkg.imports):
        return pkg.imports[-ref - 1].object_name
    return None


def verse_bindings(pkg: Package) -> dict[str, str | None]:
    """{@editable slot name: bound target name} for a placed Verse device."""
    out: dict[str, str | None] = {}
    for e in pkg.exports:
        m = _SLOT.match(e.object_name)
        if not m:
            continue
        saved = decode_properties(pkg, e).get("SavedActor")
        out[m.group(1)] = resolve_ref(pkg, saved)
    return out
