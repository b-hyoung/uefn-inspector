import shutil
from pathlib import Path

from uefn_inspector.core.properties import decode_properties
from uefn_inspector.core.uasset import read_package
from uefn_inspector.edit.write import set_enum, set_object_ref

AUDIO = Path(__file__).parent / "fixtures" / "audioplayer.uasset"
VERSE = Path(__file__).parent / "fixtures" / "versedevice.uasset"


def test_set_enum_changes_verse_vm_setting(tmp_path):
    copy = tmp_path / "a.uasset"
    shutil.copy(AUDIO, copy)
    pkg = read_package(copy)
    main = next(e for e in pkg.exports if "_UAID_" in e.object_name)
    assert "Can Be Heard By" in decode_properties(pkg, main)  # Verse-VM setting

    data = bytearray(copy.read_bytes())
    set_enum(data, pkg, main, "Can Be Heard By", "None")  # any existing name
    copy.write_bytes(bytes(data))

    pkg2 = read_package(copy)
    main2 = next(e for e in pkg2.exports if "_UAID_" in e.object_name)
    assert decode_properties(pkg2, main2)["Can Be Heard By"] == "None"


def test_set_object_ref_rewires_editable_binding(tmp_path):
    copy = tmp_path / "v.uasset"
    shutil.copy(VERSE, copy)
    pkg = read_package(copy)
    exp = next(e for e in pkg.exports
               if e.object_name.startswith("__verse_")
               and "SavedActor" in decode_properties(pkg, e))

    data = bytearray(copy.read_bytes())
    set_object_ref(data, pkg, exp, "SavedActor", -1)  # rewire to import[0]
    copy.write_bytes(bytes(data))

    pkg2 = read_package(copy)
    exp2 = next(e for e in pkg2.exports if e.object_name == exp.object_name)
    assert decode_properties(pkg2, exp2)["SavedActor"] == "obj:-1"
