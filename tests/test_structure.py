from pathlib import Path

from uefn_inspector.analysis.structure import (
    arch_lint,
    component_composition,
    outer_tree,
    soft_hard_refs,
)
from uefn_inspector.model.index import build_index
from uefn_inspector.core.uasset import read_package

AUDIO = Path(__file__).parent / "fixtures" / "audioplayer.uasset"
LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_export_has_outer_index():
    pkg = read_package(AUDIO)
    assert any(e.outer_index != 0 for e in pkg.exports)


def test_component_composition():
    comps = component_composition(read_package(AUDIO))
    assert comps and any(c.endswith("Component") for c in comps)


def test_outer_tree_non_empty():
    tree = outer_tree(read_package(AUDIO))
    assert tree  # at least one child -> parent link


def test_soft_hard_refs_split():
    refs = soft_hard_refs(read_package(AUDIO))
    assert "hard" in refs and "soft" in refs
    assert refs["hard"]


def test_arch_lint_threshold():
    idx = build_index(LEVEL_DIR)
    assert arch_lint(idx, max_components=0)       # everything with a component flagged
    assert arch_lint(idx, max_components=10_000) == []  # nothing that big
