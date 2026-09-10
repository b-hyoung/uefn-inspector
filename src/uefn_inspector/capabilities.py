"""Capability probe — what can this tool ACTUALLY do right now?

Documentation goes stale. `game-loop-kit/HARNESS.md` is a reference, not proof.
This module answers the same question by *executing* each capability against a
real file and reporting the evidence, so a session never has to trust a table.

Status values
  ok          verified by running it just now (evidence attached)
  blocked     supported, but a precondition fails right now (editor open, ...)
  unavailable not supported in this build / data missing
  unverified  could not be checked here (no sample, etc.) — do NOT claim it works
"""
from __future__ import annotations

import os
import socket
import tempfile
from pathlib import Path

_UEFN_LISTENER_PORTS = (8765, 8000)  # community uefn listener, Epic unreal-mcp


def _cap(cid, title, status, detail="", evidence=""):
    return {"id": cid, "title": title, "status": status,
            "detail": detail, "evidence": evidence}


def _port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket() as s:
        s.settimeout(0.25)
        return s.connect_ex((host, port)) == 0


def _editor_running() -> tuple[bool, str]:
    """Best-effort: a live UEFN/MCP listener means the editor is probably open,
    which means .uasset files under it may be locked for writing."""
    for p in _UEFN_LISTENER_PORTS:
        if _port_open(p):
            return True, f"listener responding on 127.0.0.1:{p}"
    return False, "no UEFN/MCP listener on 127.0.0.1:8765/8000"


def _probe_parse(sample: Path | None):
    if sample is None or not sample.exists():
        return _cap("parse_package", "패키지 파싱(.uasset/.umap)", "unverified",
                    "no sample file given", "")
    from .core.uasset import read_package
    try:
        pkg = read_package(sample)
    except Exception as e:  # pragma: no cover - defensive
        return _cap("parse_package", "패키지 파싱(.uasset/.umap)", "unavailable",
                    f"{type(e).__name__}: {e}", "")
    if not pkg.exports:
        return _cap("parse_package", "패키지 파싱(.uasset/.umap)", "unavailable",
                    "parsed but no exports", f"warnings={pkg.warnings}")
    return _cap("parse_package", "패키지 파싱(.uasset/.umap)", "ok", "",
                f"{sample.name}: names={pkg.name_count} imports={pkg.import_count} "
                f"exports={pkg.export_count}")


def _probe_properties(sample: Path | None):
    if sample is None or not sample.exists():
        return _cap("decode_properties", "프로퍼티 값 디코드", "unverified",
                    "no sample file given", "")
    from .core.properties import decode_properties
    from .core.uasset import read_package
    pkg = read_package(sample)
    decoded = total = 0
    for e in pkg.exports:
        props = decode_properties(pkg, e)
        total += len(props)
        decoded += sum(1 for v in props.values() if v is not None)
    if total == 0:
        return _cap("decode_properties", "프로퍼티 값 디코드", "unavailable",
                    "no tagged properties found", "")
    return _cap("decode_properties", "프로퍼티 값 디코드", "ok", "",
                f"{decoded}/{total} values decoded ({decoded * 100 // total}%)")


def _probe_bindings(sample: Path | None):
    if sample is None or not sample.exists():
        return _cap("read_editable_bindings", "@editable 배선 읽기 (라이브 MCP 불가)",
                    "unverified", "no sample file given", "")
    from .analysis.verse import verse_bindings
    from .core.uasset import read_package
    pkg = read_package(sample)
    b = verse_bindings(pkg)
    if not b:
        return _cap("read_editable_bindings", "@editable 배선 읽기 (라이브 MCP 불가)",
                    "unavailable", "sample has no __verse_ binding exports",
                    f"{sample.name}")
    return _cap("read_editable_bindings", "@editable 배선 읽기 (라이브 MCP 불가)",
                "ok", "", f"{len(b)} slots: {', '.join(list(b)[:4])}")


def _probe_offline_write(sample: Path | None):
    """In-place same-size write. Precondition: the editor must not hold the file."""
    open_, why = _editor_running()
    if sample is None or not sample.exists():
        return _cap("offline_write", "오프라인 값 쓰기(동일 크기)", "unverified",
                    "no sample file given", f"editor check: {why}")
    from .core.properties import property_layout
    from .core.uasset import read_package
    pkg = read_package(sample)
    writable = any(
        root in ("FloatProperty", "DoubleProperty", "IntProperty",
                 "EnumProperty", "ByteProperty", "ObjectProperty")
        for e in pkg.exports
        for (_o, _s, root) in property_layout(pkg, e).values()
    )
    if not writable:
        return _cap("offline_write", "오프라인 값 쓰기(동일 크기)", "unavailable",
                    "no writable scalar/enum/object property in sample", "")
    if open_:
        return _cap("offline_write", "오프라인 값 쓰기(동일 크기)", "blocked",
                    "UEFN editor appears to be OPEN — project files are locked; "
                    "close the editor before writing",
                    f"editor check: {why}")
    return _cap("offline_write", "오프라인 값 쓰기(동일 크기)", "ok",
                "always work on a copy / keep the .bak",
                f"writable properties present; editor check: {why}")


def _probe_add_binding(sample: Path | None):
    """Size-changing edit: verified structurally here, NOT verified in UEFN."""
    if sample is None or not sample.exists():
        return _cap("add_binding", "새 @editable 슬롯 배선 추가(크기변경)", "unverified",
                    "no sample file given", "")
    from .analysis.verse import verse_bindings
    from .core.uasset import read_package
    from .edit.add_binding import AddBindingError, add_binding
    pkg = read_package(sample)
    slots = list(verse_bindings(pkg))
    if not slots:
        return _cap("add_binding", "새 @editable 슬롯 배선 추가(크기변경)", "unavailable",
                    "sample has no binding to use as a template", "")
    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / sample.name
        copy.write_bytes(sample.read_bytes())
        probe_slot = "__probe_capability__"
        try:
            add_binding(copy, slot=probe_slot, template_slot=slots[0], backup=False)
        except AddBindingError as e:
            return _cap("add_binding", "새 @editable 슬롯 배선 추가(크기변경)",
                        "unavailable", str(e), "")
        after = verse_bindings(read_package(copy))
    if probe_slot not in after:
        return _cap("add_binding", "새 @editable 슬롯 배선 추가(크기변경)",
                    "unavailable", "slot did not appear after add", "")
    return _cap("add_binding", "새 @editable 슬롯 배선 추가(크기변경)", "ok",
                "⚠️ UEFN acceptance of resized packages is NOT verified — copy first",
                f"probe added a slot on a temp copy ({len(slots)} existing)")


def _probe_engine_catalog():
    from .analysis.engine_catalog import CatalogMissing, load_engine_catalog
    try:
        cat = load_engine_catalog()
    except CatalogMissing:
        return _cap("engine_catalog", "엔진 디바이스 카탈로그", "unavailable",
                    "not generated on this machine — see cue4parse_cli/README.md", "")
    return _cap("engine_catalog", "엔진 디바이스 카탈로그", "ok", "",
                f"{cat.get('deviceCount', 0)} devices")


def _probe_live_editor():
    open_, why = _editor_running()
    if open_:
        return _cap("live_editor", "라이브 조작·PIE(다른 MCP 담당)", "ok",
                    "use the uefn / unreal-mcp servers for runtime work", why)
    return _cap("live_editor", "라이브 조작·PIE(다른 MCP 담당)", "blocked",
                "UEFN editor not running — behavioral verification impossible now", why)


def probe(sample: str | Path | None = None) -> dict:
    """Run every capability check and report what actually holds right now."""
    s = Path(sample) if sample else None
    caps = [
        _probe_parse(s),
        _probe_properties(s),
        _probe_bindings(s),
        _probe_offline_write(s),
        _probe_add_binding(s),
        _probe_engine_catalog(),
        _probe_live_editor(),
    ]
    counts: dict[str, int] = {}
    for c in caps:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    return {
        "sample": str(s) if s else None,
        "cwd": os.getcwd(),
        "capabilities": caps,
        "summary": counts,
        "note": ("Executed checks — not documentation. 'ok' means it ran just now. "
                 "Never claim a capability reported as unverified/unavailable."),
    }
