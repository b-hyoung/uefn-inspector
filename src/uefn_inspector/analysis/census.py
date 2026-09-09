"""Census / lint / extraction analyses over a ProjectIndex.

Generic — no project-specific assumptions.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from uefn_inspector.model.index import ProjectIndex
from uefn_inspector.core.uasset import Package


def type_census(index: ProjectIndex) -> Counter:
    """Distribution of imported class types across the project."""
    c: Counter = Counter()
    for pkg in index.packages.values():
        for imp in pkg.imports:
            if imp.class_name:
                c[imp.class_name] += 1
    return c


def external_deps(index: ProjectIndex) -> Counter:
    """Referenced mount roots (e.g. /Script, /Game, /CRD_AudioPlayer)."""
    c: Counter = Counter()
    for pkg in index.packages.values():
        for imp in pkg.imports:
            p = imp.class_package
            if p.startswith("/") and "/" in p[1:]:
                c["/" + p[1:].split("/", 1)[0]] += 1
            elif p.startswith("/"):
                c[p] += 1
    return c


def naming_lint(items: list[str], pattern: str) -> list[str]:
    """Items that do NOT match the expected naming pattern."""
    rx = re.compile(pattern)
    return [i for i in items if not rx.search(i)]


def extract_strings(pkg: Package) -> list[str]:
    """Human-readable strings from the name table (multi-word labels, not paths)."""
    return sorted(
        n for n in pkg.names
        if " " in n and not n.startswith("/")
    )


def size_report(index: ProjectIndex) -> dict[str, int]:
    """Byte size per indexed file."""
    out: dict[str, int] = {}
    for path in index.packages:
        try:
            out[path] = Path(path).stat().st_size
        except OSError:
            out[path] = 0
    return out


def _all_refs(index: ProjectIndex) -> set[str]:
    refs: set[str] = set()
    for pkg in index.packages.values():
        refs |= {n for n in pkg.names if n.startswith("/") and not n.startswith("/Script")}
    return refs


def cross_level_shared(index_a: ProjectIndex, index_b: ProjectIndex) -> set[str]:
    """Content targets referenced by both indexes (shared assets)."""
    return _all_refs(index_a) & _all_refs(index_b)


def engine_version_census(index: ProjectIndex) -> Counter:
    """Distribution of (UE4/UE5) file versions across parsed packages."""
    c: Counter = Counter()
    for pkg in index.packages.values():
        if pkg.tag:  # parsed a real header
            c[f"{pkg.file_version_ue4}/{pkg.file_version_ue5}"] += 1
    return c


_TAG = re.compile(r"^[A-Za-z][\w]*(?:\.[A-Za-z][\w]*)+$")


def gameplay_tag_census(index: ProjectIndex) -> Counter:
    """Dotted identifiers that look like GameplayTags (heuristic)."""
    c: Counter = Counter()
    for pkg in index.packages.values():
        for n in pkg.names:
            if "/" not in n and " " not in n and "::" not in n and _TAG.match(n):
                c[n] += 1
    return c
