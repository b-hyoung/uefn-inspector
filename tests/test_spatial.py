from pathlib import Path

from uefn_inspector.index import build_index
from uefn_inspector.properties import property_census
from uefn_inspector.spatial import (
    density_grid,
    min_spacing,
    spatial_bounds,
    spatial_extent,
)

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_spatial_bounds():
    assert spatial_bounds([(0, 0, 0), (10, 20, 30)]) == ((0, 0, 0), (10, 20, 30))


def test_spatial_extent():
    assert spatial_extent([(0, 0, 0), (10, 20, 30)]) == (10, 20, 30)


def test_min_spacing_pythagorean():
    assert min_spacing([(0, 0, 0), (3, 4, 0), (100, 0, 0)]) == 5.0


def test_density_grid_buckets():
    g = density_grid([(0, 0, 0), (1, 1, 0), (100, 0, 0)], cell=10)
    assert g[(0, 0, 0)] == 2
    assert g[(100, 0, 0)] == 1


def test_property_census_on_level():
    c = property_census(build_index(LEVEL_DIR))
    assert c.get("RelativeLocation", 0) > 0
