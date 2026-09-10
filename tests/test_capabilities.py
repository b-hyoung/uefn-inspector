"""The capability probe must report what is ACTUALLY possible right now.

It exists because documentation lies: HARNESS.md can go stale, and a session
that trusts it will plan on capabilities that do not hold in this environment.
Every entry must therefore come from an executed check, not from a table.
"""
from pathlib import Path

from uefn_inspector.capabilities import probe

FIX = Path(__file__).parent / "fixtures"


def test_probe_reports_verified_capabilities():
    r = probe(sample=FIX / "versedevice.uasset")
    caps = {c["id"]: c for c in r["capabilities"]}

    # things we know work — must be reported as verified by execution
    for cid in ("parse_package", "decode_properties", "read_editable_bindings"):
        assert caps[cid]["status"] == "ok", caps[cid]
        assert caps[cid]["evidence"], "no evidence recorded"


def test_probe_marks_unavailable_without_sample():
    r = probe(sample=None)
    caps = {c["id"]: c for c in r["capabilities"]}
    # with no sample file these cannot be verified — must NOT claim ok
    assert caps["parse_package"]["status"] in {"unverified", "unavailable"}


def test_probe_reports_offline_write_precondition():
    r = probe(sample=FIX / "versedevice.uasset")
    caps = {c["id"]: c for c in r["capabilities"]}
    w = caps["offline_write"]
    # editor-open is a real precondition; the probe must state it either way
    assert w["status"] in {"ok", "blocked"}
    assert "editor" in (w["detail"] + w["evidence"]).lower()


def test_probe_never_claims_unverified_things():
    r = probe(sample=FIX / "versedevice.uasset")
    for c in r["capabilities"]:
        assert c["status"] in {"ok", "blocked", "unverified", "unavailable"}
        if c["status"] == "ok":
            assert c["evidence"], f"{c['id']} claims ok with no evidence"
