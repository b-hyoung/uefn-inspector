"""Offline level/actor inventory built on top of the faithful .uasset model."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .uasset import Package, read_package


@dataclass
class PlacedActor:
    device_class: str = ""
    asset_refs: list[str] = field(default_factory=list)


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
    return PlacedActor(device_class=_device_class(pkg), asset_refs=asset_refs)
