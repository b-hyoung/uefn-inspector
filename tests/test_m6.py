from pathlib import Path

from uefn_inspector.analyze import (
    dependency_depth,
    fan_out,
    hotspots,
    to_mermaid,
)
from uefn_inspector.census import (
    cross_level_shared,
    external_deps,
    extract_strings,
    naming_lint,
    size_report,
    type_census,
)
from uefn_inspector.index import ProjectIndex, build_index
from uefn_inspector.level import Level, PlacedActor, find_duplicates, verse_devices
from uefn_inspector.uasset import Package, read_package

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"
AUDIO = Path(__file__).parent / "fixtures" / "audioplayer.uasset"


# --- graph metrics ---
def test_hotspots_sorted_desc():
    hs = hotspots(build_index(LEVEL_DIR))
    assert hs and hs[0][1] >= 1
    counts = [c for _, c in hs]
    assert counts == sorted(counts, reverse=True)


def test_fan_out_counts():
    fo = fan_out(build_index(LEVEL_DIR))
    assert any(c > 0 for c in fo.values())


def test_dependency_depth_longest_chain():
    assert dependency_depth({"A": ["B"], "B": ["C"], "C": []}) == 3


def test_to_mermaid_is_graph():
    m = to_mermaid(build_index(LEVEL_DIR))
    assert m.startswith("graph") and "-->" in m


# --- census / lint ---
def test_type_census_has_bp_generated_class():
    c = type_census(build_index(LEVEL_DIR))
    assert c.get("BlueprintGeneratedClass", 0) > 0


def test_external_deps_by_mount():
    d = external_deps(build_index(LEVEL_DIR))
    assert "/Script" in d


def test_naming_lint_flags_violations():
    assert naming_lint(["WID_Gun", "badname"], r"^WID_") == ["badname"]


def test_extract_strings_human_readable():
    strings = extract_strings(read_package(AUDIO))
    assert "Can Be Heard By" in strings


def test_size_report():
    r = size_report(build_index(LEVEL_DIR))
    assert len(r) == 3 and all(v > 0 for v in r.values())


def test_cross_level_shared():
    a = ProjectIndex(packages={"f": Package(names=["/X/shared", "/X/onlyA"])})
    b = ProjectIndex(packages={"g": Package(names=["/X/shared", "/X/onlyB"])})
    shared = cross_level_shared(a, b)
    assert "/X/shared" in shared and "/X/onlyA" not in shared


# --- level based ---
def test_find_duplicates():
    lvl = Level(actors=[PlacedActor(device_class="X"), PlacedActor(device_class="X"),
                        PlacedActor(device_class="Y")])
    dups = find_duplicates(lvl)
    assert dups["X"] == 2 and "Y" not in dups


def test_verse_devices():
    lvl = Level(actors=[PlacedActor(device_class="VerseDevice_C"),
                        PlacedActor(device_class="Device_X")])
    vd = verse_devices(lvl)
    assert len(vd) == 1 and vd[0].device_class == "VerseDevice_C"
