"""Static structural analysis of Verse (.verse) source text.

Extracts the *structure* a Verse device declares — class, base, @editable
slots (name/type/default), functions, imports — NOT the runtime semantics of
the code. This complements the on-disk @editable *bindings* read from .uasset:
.verse says which slots exist; .uasset says what they're wired to.
"""
from __future__ import annotations

import re

_CLASS = re.compile(r"(\w+)\s*:=\s*class\((\w+)\)")
# @editable on its own line, then  NAME : TYPE = DEFAULT
_EDITABLE = re.compile(r"@editable\s*\n\s*(\w+)\s*:\s*(\S+)\s*=\s*(.+)")
_USING = re.compile(r"using\s*\{\s*([^}]+?)\s*\}")
# function/event: NAME<...>(...) ... :Type=   (has parens, unlike editables)
_FUNC = re.compile(r"^\s+(\w+)(?:<[^>]*>)?\s*\([^)]*\)", re.MULTILINE)


def parse_verse(text: str) -> dict:
    m = _CLASS.search(text)
    class_name = m.group(1) if m else ""
    base_class = m.group(2) if m else ""

    editables = [
        {"name": n, "type": t, "default": d.strip()}
        for n, t, d in _EDITABLE.findall(text)
    ]

    functions = sorted(set(_FUNC.findall(text)))
    usings = [u.strip() for u in _USING.findall(text)]

    return {
        "class_name": class_name,
        "base_class": base_class,
        "editables": editables,
        "functions": functions,
        "usings": usings,
    }


def device_slots(verse_info: dict) -> list[str]:
    """@editable slots that reference devices (need wiring in the editor)."""
    return [e["name"] for e in verse_info["editables"] if e["type"].endswith("_device")]


def cross_reference(verse_info: dict, bindings: dict) -> dict:
    """Declared device slots (.verse) vs actual wiring (.uasset bindings).

    Surfaces slots declared in code but left UNWIRED — a common silent bug.
    """
    slots = device_slots(verse_info)
    return {
        "wired": [s for s in slots if bindings.get(s)],
        "unwired": [s for s in slots if not bindings.get(s)],
    }
