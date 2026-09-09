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
