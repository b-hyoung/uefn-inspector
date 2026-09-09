"""CLI: offline inventory report for a UEFN level / actor directory."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .level import inspect_level


def run(path: str | Path) -> dict:
    """Build the report data for a level/actor directory."""
    level = inspect_level(path)
    devices = Counter(a.device_class for a in level.actors if a.device_class)
    asset_refs = sorted({r for a in level.actors for r in a.asset_refs})
    return {
        "level": level.name,
        "actor_count": len(level.actors),
        "devices": dict(devices.most_common()),
        "asset_refs": asset_refs,
        "warnings": level.warnings,
    }


def _print_report(report: dict) -> None:
    print(f"레벨: {report['level']}   (액터 {report['actor_count']}개)")
    print("\n배치 디바이스:")
    for cls, count in report["devices"].items():
        print(f"  {count:3d} x {cls}")
    audio = [r for r in report["asset_refs"] if "/Audio/" in r or "Sound" in r]
    if audio:
        print("\n참조 오디오:")
        for a in audio:
            print(f"  {a}")
    if report["warnings"]:
        print(f"\n경고 {len(report['warnings'])}건 (파싱 실패 파일)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uefn_inspector",
        description="에디터 없이 UEFN 레벨(.uasset)을 오프라인 분석한다.",
    )
    parser.add_argument("path", help="레벨/액터 디렉터리 (예: .../__ExternalActors__/Level/PointLevel)")
    parser.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = parser.parse_args(argv)

    if not Path(args.path).exists():
        print(f"경로 없음: {args.path}", file=sys.stderr)
        return 2

    report = run(args.path)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_report(report)
    return 0
