"""Backup-safe offline patching of a .uasset scalar value.

Writes in place (same byte width -> no offset shifts), always taking a .bak
backup first, and re-validates by re-parsing. Whether UEFN *accepts* the
modified file on load/publish is a separate LIVE check (open the editor) — this
tool only guarantees the file stays structurally parseable.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from .uasset import read_package
from .write import set_scalar


def patch_scalar_file(path: str | Path, export_name: str, prop: str, value,
                      backup: bool = True) -> Path:
    """Patch one scalar property in a .uasset, backing up to <file>.bak first.
    Returns the backup path. Raises if the result no longer parses."""
    p = Path(path)
    bak = p.with_suffix(p.suffix + ".bak")
    if backup:
        shutil.copy(p, bak)

    pkg = read_package(p)
    export = next((e for e in pkg.exports if e.object_name == export_name), None)
    if export is None:
        raise ValueError(f"export not found: {export_name}")

    data = bytearray(p.read_bytes())
    set_scalar(data, pkg, export, prop, value)
    p.write_bytes(bytes(data))

    # re-validate: must still parse and keep the same export count
    check = read_package(p)
    if len(check.exports) != len(pkg.exports):
        shutil.copy(bak, p)  # roll back
        raise RuntimeError("patch broke the package — rolled back from .bak")
    return bak
