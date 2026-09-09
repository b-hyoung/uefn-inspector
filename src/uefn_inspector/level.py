"""Offline level/actor inventory built on top of the faithful .uasset model."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .uasset import Package, read_package


@dataclass
class PlacedActor:
    device_class: str = ""
    name: str = ""
    asset_refs: list[str] = field(default_factory=list)


@dataclass
class Level:
    name: str = ""
    actors: list[PlacedActor] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _device_class(pkg: Package) -> str:
    # The placed actor export carries a "_UAID_" suffix; its class_index is a
    # negative FPackageIndex into the import table -> the real device class.
    for exp in pkg.exports:
        if "_UAID_" in exp.object_name and exp.class_index < 0:
            imp_idx = -exp.class_index - 1
            if 0 <= imp_idx < len(pkg.imports):
                return pkg.imports[imp_idx].object_name
    # Fallback (heuristic) when the export/import maps did not parse.
    return next((n.split("_UAID_")[0] for n in pkg.names if "_UAID_" in n), "")


def inspect_actor(path: str | Path) -> PlacedActor:
    pkg = read_package(path)
    asset_refs = [n for n in pkg.names if n.startswith("/") and not n.startswith("/Script")]
    name = next((e.object_name for e in pkg.exports if "_UAID_" in e.object_name), "")
    return PlacedActor(device_class=_device_class(pkg), name=name, asset_refs=asset_refs)


def inspect_level(path: str | Path) -> Level:
    """Scan a directory of .uasset actor files (UEFN OFPA layout) into a Level."""
    root = Path(path)
    actors: list[PlacedActor] = []
    warnings: list[str] = []
    for f in sorted(root.rglob("*.uasset")):
        try:
            actors.append(inspect_actor(f))
        except Exception as exc:  # keep going on a bad file (spec: graceful)
            warnings.append(f"{f.name}: {exc}")
    return Level(name=root.name, actors=actors, warnings=warnings)


def audit_level(path: str | Path) -> dict:
    """Health summary of a level: device counts, duplicate actor names, warnings.

    broken_refs needs a full project asset index (assets, not just placed
    actors), so it is left empty here with a note rather than reported noisily.
    """
    level = inspect_level(path)
    device_counts = dict(
        Counter(a.device_class for a in level.actors if a.device_class).most_common()
    )
    name_counts = Counter(a.name for a in level.actors if a.name)
    duplicate_names = sorted(n for n, c in name_counts.items() if c > 1)
    return {
        "level": level.name,
        "actor_count": len(level.actors),
        "device_counts": device_counts,
        "duplicate_names": duplicate_names,
        "broken_refs": [],
        "broken_refs_note": "requires full project asset index (not just actors)",
        "warnings": level.warnings,
    }


def diff_levels(a: Level, b: Level) -> dict:
    """Structural diff by device-class multiset. Empty when identical."""
    ca = Counter(x.device_class for x in a.actors)
    cb = Counter(x.device_class for x in b.actors)
    return {"added": dict(cb - ca), "removed": dict(ca - cb)}


def find_duplicates(level: Level) -> dict[str, int]:
    """Device classes placed more than once."""
    counts = Counter(a.device_class for a in level.actors if a.device_class)
    return {cls: n for cls, n in counts.items() if n > 1}


def verse_devices(level: Level) -> list[PlacedActor]:
    """Placed actors that are Verse devices."""
    return [a for a in level.actors if "VerseDevice" in a.device_class]


def actor_diff(a: Level, b: Level) -> dict[str, list[str]]:
    """Which named actors were added / removed between two levels."""
    na = {x.name for x in a.actors if x.name}
    nb = {x.name for x in b.actors if x.name}
    return {"added": sorted(nb - na), "removed": sorted(na - nb)}
