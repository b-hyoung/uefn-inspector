from pathlib import Path

from uefn_inspector.analyze import to_dot, transitive_reachable
from uefn_inspector.census import engine_version_census, gameplay_tag_census
from uefn_inspector.index import ProjectIndex, build_index
from uefn_inspector.level import Level, PlacedActor, actor_diff
from uefn_inspector.uasset import Package

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_actor_diff_by_name():
    a = Level(actors=[PlacedActor(name="A"), PlacedActor(name="B")])
    b = Level(actors=[PlacedActor(name="A")])
    d = actor_diff(a, b)
    assert "B" in d["removed"] and d["added"] == []


def test_transitive_reachable():
    reach = transitive_reachable({"A": ["B"], "B": ["C"], "C": []}, "A")
    assert reach == {"B", "C"}


def test_to_dot():
    dot = to_dot(build_index(LEVEL_DIR))
    assert dot.startswith("digraph") and "->" in dot


def test_engine_version_census():
    c = engine_version_census(build_index(LEVEL_DIR))
    assert c and all(v > 0 for v in c.values())


def test_gameplay_tag_census():
    idx = ProjectIndex(packages={
        "f": Package(names=["GameplayCue.Foo", "NotATag", "/some/path"])
    })
    assert gameplay_tag_census(idx).get("GameplayCue.Foo", 0) == 1
