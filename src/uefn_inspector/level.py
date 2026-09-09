"""Offline level/actor inventory built on top of the .uasset reader."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .uasset import read_package


@dataclass
class PlacedActor:
    device_class: str = ""
    asset_refs: list[str] = field(default_factory=list)


def inspect_actor(path: str | Path) -> PlacedActor:
    pkg = read_package(path)

    # The placed actor instance is named "<DeviceClass>_UAID_<hash>"; strip the
    # UAID suffix to recover the device class it was spawned from.
    device_class = next(
        (n.split("_UAID_")[0] for n in pkg.names if "_UAID_" in n),
        "",
    )
    asset_refs = [n for n in pkg.names if n.startswith("/") and not n.startswith("/Script")]

    return PlacedActor(device_class=device_class, asset_refs=asset_refs)
