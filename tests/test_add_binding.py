"""Adding a NEW @editable binding slot (size-changing edit).

A placed Verse device stores each wired slot as a `__verse_0x<hash>_<Slot>`
sub-object export whose SavedActor points at the bound actor. Wiring a slot
that was never wired therefore means *adding* an export (and its name) —
a size-changing edit, unlike set_object_ref which only rewrites a pointer.
"""
import shutil
from pathlib import Path

from uefn_inspector.analysis.verse import verse_bindings
from uefn_inspector.core.uasset import read_package
from uefn_inspector.edit.add_binding import add_binding

VERSE = Path(__file__).parent / "fixtures" / "versedevice.uasset"


def test_add_binding_creates_new_slot(tmp_path):
    src = tmp_path / "v.uasset"
    shutil.copy(VERSE, src)

    before = verse_bindings(read_package(src))
    assert "HeartMid" not in before
    template_target = before["HeartFar"]  # bind the new slot to the same actor

    add_binding(src, slot="HeartMid", template_slot="HeartFar")

    pkg = read_package(src)
    after = verse_bindings(pkg)
    assert "HeartMid" in after, "new slot not present"
    assert after["HeartMid"] == template_target
    # existing wiring must survive untouched
    for slot, target in before.items():
        assert after[slot] == target
    # package integrity: one more export, all serial regions in range
    n = src.stat().st_size
    assert len(pkg.exports) == len(read_package(VERSE).exports) + 1
    for e in pkg.exports:
        assert 0 < e.serial_offset and e.serial_offset + e.serial_size <= n
