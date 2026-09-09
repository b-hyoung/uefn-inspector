from pathlib import Path

from uefn_inspector.analyze import (
    find_broken_refs,
    find_cycles,
    find_orphans,
    impact,
)
from uefn_inspector.index import build_index

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


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
