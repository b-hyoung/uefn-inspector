from pathlib import Path

from uefn_inspector.analysis.analyze import (
    curve_usage,
    find_broken_refs,
    find_cycles,
    find_orphans,
    impact,
    material_usage,
    mesh_usage,
)
from uefn_inspector.model.index import ProjectIndex, build_index
from uefn_inspector.core.uasset import ObjectImport, Package

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def _index_with(imports):
    return ProjectIndex(packages={"f1": Package(imports=list(imports))})


def test_find_cycles_detects_and_ignores():
    assert find_cycles({"A": ["B"], "B": ["A"], "C": []})  # has a cycle
    assert find_cycles({"A": ["B"], "B": ["C"], "C": []}) == []  # acyclic


def test_impact_includes_referencer():
    idx = build_index(LEVEL_DIR)
    assert any("audioplayer" in p.lower() for p in impact(idx, "Heartbeat_Near"))


def test_find_orphans():
    orphans = find_orphans({"A", "B", "C"}, {"A": {"B"}})
    assert "C" in orphans        # referenced by nobody
    assert "B" not in orphans    # referenced by A


def test_find_broken_refs():
    broken = find_broken_refs(
        known={"/X/a"},
        references={"/X/a", "/X/missing", "/Script/z"},
    )
    assert broken == ["/X/missing"]


def test_mesh_usage_excludes_components():
    idx = _index_with([
        ObjectImport(class_name="StaticMesh", object_name="SM_Wall"),
        ObjectImport(class_name="StaticMeshComponent", object_name="Comp0"),
    ])
    usage = mesh_usage(idx)
    assert usage["SM_Wall"] == ["f1"]
    assert "Comp0" not in usage


def test_material_usage():
    idx = _index_with([
        ObjectImport(class_name="MaterialInstanceConstant", object_name="MI_Red"),
    ])
    assert material_usage(idx)["MI_Red"] == ["f1"]


def test_curve_usage():
    idx = _index_with([ObjectImport(class_name="CurveFloat", object_name="C_Falloff")])
    assert curve_usage(idx)["C_Falloff"] == ["f1"]
