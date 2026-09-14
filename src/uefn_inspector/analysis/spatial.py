"""Spatial analyses over decoded actor locations (unlocked by property decode).

Pure functions on lists of (x, y, z) tuples — generic, no project assumptions.
"""
from __future__ import annotations

import math

Loc = tuple[float, float, float]


def spatial_bounds(locations: list[Loc]) -> tuple[Loc, Loc] | None:
    """(min_xyz, max_xyz). None if no locations."""
    if not locations:
        return None
    xs, ys, zs = zip(*locations)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def spatial_extent(locations: list[Loc]) -> Loc | None:
    """Size of the bounding box (max - min per axis)."""
    b = spatial_bounds(locations)
    if b is None:
        return None
    (lo, hi) = b
    return (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])


def min_spacing(locations: list[Loc]) -> float | None:
    """Smallest pairwise distance (O(n^2); fine for level-sized inputs)."""
    if len(locations) < 2:
        return None
    best = math.inf
    for i in range(len(locations)):
        ax, ay, az = locations[i]
        for j in range(i + 1, len(locations)):
            bx, by, bz = locations[j]
            d = math.dist((ax, ay, az), (bx, by, bz))
            if d < best:
                best = d
    return best


def density_grid(locations: list[Loc], cell: float = 512.0) -> dict[tuple, int]:
    """Count actors per grid cell of size `cell` (clustering / heat map)."""
    grid: dict[tuple, int] = {}
    for x, y, z in locations:
        key = (
            math.floor(x / cell) * int(cell),
            math.floor(y / cell) * int(cell),
            math.floor(z / cell) * int(cell),
        )
        grid[key] = grid.get(key, 0) + 1
    return grid


def _symbols(labels: list[str]) -> dict[str, str]:
    """One printable symbol per distinct label: first letter of the class stem
    ("Device_GuardSpawner_C" -> "G"), then later letters, then digits."""
    out: dict[str, str] = {}
    taken: set[str] = set()
    for label in labels:
        if label in out:
            continue
        stem = label.replace("Device_", "").replace("GrayBox_", "").lstrip("_") or label
        candidates = [c.upper() for c in stem if c.isalpha()] + list("0123456789")
        sym = next((c for c in candidates if c not in taken), "?")
        taken.add(sym)
        out[label] = sym
    return out


def ascii_map(items: list[tuple[str, Loc]], cell: float = 500.0, max_cols: int = 80) -> dict:
    """Top-down text map of labelled points (x -> columns, y -> rows, z ignored).

    A cell holding one actor shows its symbol; several actors of one kind show
    the count (2-9, "+" beyond); mixed kinds show "*". Returns the map, the
    symbol legend, the cell size actually used and the xyz bounds.
    """
    if not items:
        return {"map": "", "legend": {}, "cell": cell, "bounds": None}
    locs = [loc for _, loc in items]
    (lo, hi) = spatial_bounds(locs)
    cols = int((hi[0] - lo[0]) // cell) + 1
    if cols > max_cols:                       # coarsen until it fits one screen
        cell = (hi[0] - lo[0]) / (max_cols - 1)
        cols = max_cols
    rows = int((hi[1] - lo[1]) // cell) + 1
    legend = _symbols([label for label, _ in items])
    grid: dict[tuple[int, int], list[str]] = {}
    for label, (x, y, _z) in items:
        key = (int((y - lo[1]) // cell), int((x - lo[0]) // cell))
        grid.setdefault(key, []).append(legend[label])
    lines = [f"cell={cell:g}  x: {lo[0]:g} .. {hi[0]:g}  y: {lo[1]:g} .. {hi[1]:g}  (row = y, col = x)"]
    for r in range(rows):
        chars = []
        for c in range(cols):
            syms = grid.get((r, c))
            if not syms:
                chars.append(".")
            elif len(set(syms)) > 1:
                chars.append("*")
            elif len(syms) == 1:
                chars.append(syms[0])
            else:
                chars.append(str(len(syms)) if len(syms) <= 9 else "+")
        lines.append(f"{lo[1] + r * cell:>8g} |" + "".join(chars))
    return {"map": "\n".join(lines), "legend": {v: k for k, v in legend.items()},
            "cell": cell, "bounds": (lo, hi)}
