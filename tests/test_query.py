from pathlib import Path

from uefn_inspector.index import build_index
from uefn_inspector.query import search, where_used

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_search_finds_audioplayer():
    idx = build_index(LEVEL_DIR)
    hits = search(idx, "AudioPlayer")
    assert any("audioplayer" in p.lower() for p in hits)


def test_where_used_finds_sound_referencer():
    idx = build_index(LEVEL_DIR)
    users = where_used(idx, "Heartbeat_Near")
    assert any("audioplayer" in p.lower() for p in users)
