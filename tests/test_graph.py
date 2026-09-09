from pathlib import Path

from uefn_inspector.graph import build_reference_graph
from uefn_inspector.index import build_index

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_reference_graph_links_audioplayer_to_sound():
    idx = build_index(LEVEL_DIR)
    g = build_reference_graph(idx)
    ap = next(p for p in idx.packages if "audioplayer" in p.lower())
    assert any("Heartbeat_Near" in target for target in g.forward[ap])
