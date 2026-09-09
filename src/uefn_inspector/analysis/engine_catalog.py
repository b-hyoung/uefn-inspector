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


def load_engine_catalog(path: str | Path | None = None) -> dict:
    return json.loads(Path(path or _DEFAULT).read_text(encoding="utf-8"))


def search_engine_devices(query: str, catalog: dict | None = None) -> list[str]:
    cat = catalog or load_engine_catalog()
    q = query.lower()
    return [d for d in cat["devices"] if q in d.lower()]
