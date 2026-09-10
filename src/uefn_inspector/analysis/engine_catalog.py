"""Access the offline-extracted UEFN engine device catalog.

The catalog (data/engine_device_catalog.json) is produced by the CUE4Parse CLI
(see cue4parse_cli/README) mounting Fortnite paks — 1119 creative device
classes, readable without opening the editor. This is the "what devices exist"
answer that the editor's search could not give offline.
"""
from __future__ import annotations

import json
from pathlib import Path

_DEFAULT = Path(__file__).resolve().parents[3] / "data" / "engine_device_catalog.json"


class CatalogMissing(FileNotFoundError):
    """The engine device catalog has not been generated on this machine."""


_MISSING_HELP = (
    "Engine device catalog not found at {path}.\n"
    "It is NOT shipped with this repo (it is derived from your own Fortnite "
    "install). Generate it yourself:\n"
    "  see cue4parse_cli/README.md — mount your Fortnite paks with the "
    "CUE4Parse CLI and write data/engine_device_catalog.json\n"
    "Every other tool in uefn-inspector works without it."
)


def load_engine_catalog(path: str | Path | None = None) -> dict:
    p = Path(path or _DEFAULT)
    if not p.exists():
        raise CatalogMissing(_MISSING_HELP.format(path=p))
    return json.loads(p.read_text(encoding="utf-8"))


def search_engine_devices(query: str, catalog: dict | None = None) -> list[str]:
    cat = catalog or load_engine_catalog()
    q = query.lower()
    return [d for d in cat["devices"] if q in d.lower()]
