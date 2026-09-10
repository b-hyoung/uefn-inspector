# uefn-inspector

**UEFN(.uasset/.umap) 오프라인 분석·편집 도구.** 에디터를 켜지 않고 — 혹은 에디터가
다른 작업 중일 때도 — 프로젝트 파일을 직접 파싱해서 "무엇이 배치·연결·설정됐는지"를
읽고, 값을 안전하게 수정한다. 기존 UEFN MCP(라이브 리플렉션)가 **못 하던** Verse-VM
설정·`@editable` 배선까지 파일에서 직접 읽고 쓴다.

- Python 3.11+ · 외부 파싱 의존성 없음(stdlib `struct`) · 70 tests green
- 실행: `<py> -m uefn_inspector <레벨/액터 디렉터리>`  (py = `C:/Users/ACE/AppData/Local/Programs/Python/Python311/python.exe`)

---

## 어떻게 소비하나 (MCP vs MD)

| 방식 | 용도 | 상태 |
|---|---|---|
| **라이브러리 / CLI** | 지금 바로 분석·리포트 | ✅ 현재 |
| **MCP 도구 래퍼** (권장 주 인터페이스) | 아무 Claude 세션에서 실시간 질의 (`inspect_level`·`read_actor` 등 7개) | ✅ `mcp_server.py` |
| **MD/JSON 리포트** | 스냅샷·핸드오프 (커밋·나중에 읽기) | ✅ CLI `--json` |

**권장:** 분석들을 **MCP 도구로 노출**해 세션에서 호출 + 필요 시 MD/JSON 리포트로 스냅샷.
기존 라이브 MCP(uefn/unreal)와 **상호보완**: 라이브 MCP=물리 배치 조작, uefn-inspector=오프라인 로직/값 읽기·쓰기.

## 빠른 시작
```bash
# 레벨 인벤토리 (사람용 / JSON)
<py> -m uefn_inspector "<프로젝트>/Content/__ExternalActors__/Level/<레벨>"
<py> -m uefn_inspector "<...>/PointLevel" --json
```

## 무엇이 되나 (요약 — 상세는 docs/CAPABILITIES.md)
- **읽기(오프라인):** 인벤토리 · 검색 · where-used · 의존/순환/영향/고아 · census · 공간분석 · 프로퍼티 값(**91% 디코드**) · **Verse-VM 설정값·@editable 배선** · `.verse` 구조↔배선 교차검증
- **쓰기(오프라인, UEFN 수용 검증됨):** 스칼라·enum·오브젝트참조 **동일크기 in-place**(백업+롤백). 크기변경 편집은 fixup 엔진(토대만)
- **엔진 콘텐츠:** CUE4Parse CLI로 Fortnite 마운트 → 디바이스 카탈로그 (심층값은 usmap 필요)
  ⚠️ 카탈로그(`data/engine_device_catalog.json`)는 **저장소에 없다** — Fortnite 파생물이라 재배포 안 함.
  직접 생성: `cue4parse_cli/README.md`. **없어도 `engine_devices` 외 모든 도구는 동작한다.**
- **천장/제약:** 크기변경 쓰기 미완 · usmap 외부 막힘 · Verse 코드 "의미" 해석은 범위 밖

## 모듈 지도 (`src/uefn_inspector/` — 레이어별 하위패키지)
```
core/      파싱 코어
  uasset.py       .uasset/.umap → names/imports/exports(serial 영역)
  properties.py   태그드 프로퍼티 값 디코드(UE5.4 FPropertyTypeName)
model/     프로젝트 모델
  index.py        전 파일 인덱스        graph.py  참조 그래프(forward/reverse)
analysis/  분석
  query.py        검색·where-used·설정발견
  analyze.py      순환·영향·고아·깨진참조·hotspot·fan-out·의존깊이·mermaid/DOT·mesh/mat/curve
  census.py       타입·외부의존·엔진버전·tag census·네이밍린트·문자열추출
  structure.py    컴포넌트구성·outer트리·soft/hard참조·아키텍처린트
  spatial.py      bounds·density·spacing            verse.py  @editable 배선 읽기
  verse_source.py .verse 구조분석+교차검증          engine_catalog.py  엔진 카탈로그 검색
edit/      쓰기(B)
  write.py  값 in-place 쓰기   patch.py  백업+롤백 파일패치   rebuild.py  크기변경 fixup(토대)
(top)      level.py  인벤토리·audit·diff    cli.py  CLI    __main__.py
```

## MCP 서버 (`mcp_server.py`)
분석을 MCP 도구로 노출 — 아무 Claude 세션에서 호출. 도구:
`inspect_level` · `audit` · `find` · `who_uses` · `read_actor`(Verse-VM 값 포함) · `editable_bindings` · `engine_devices`
```bash
claude mcp add uefn-inspector -s user -- <py> <abs>/mcp_server.py
```

## 게임 루프 엔지니어링 (`game-loop-kit/`)
uefn-inspector를 엔진 삼아 UEFN 게임을 **A-Z 루프**로 구축하는 범용 템플릿.
**Plan→Task→Ticket** 계층 + 구조검증(inspector)/행동검증(PIE). → `game-loop-kit/README.md`

## 문서
- `docs/CAPABILITIES.md` — 되는것/안되는것 확정표
- `docs/ROADMAP.md` — 완성 구조·마일스톤
- `docs/BACKLOG.md` — 티켓 보드(자율 루프용)
- `docs/capability-matrix.md` · `docs/context.md`(동기·범용성 원칙) · `docs/explainer.html`(시각 설명)
- `cue4parse_cli/README.md` — 엔진 디바이스 카탈로그 **직접 생성 가이드**(AES·config·코드·한계)

## 테스트
```bash
<py> -m pytest -q     # 70 tests
```
> 픽스처(`tests/fixtures/`)는 사용자 프로젝트에서 복사한 UEFN 콘텐츠라 git 미포함(로컬 재현).

## 원칙
**범용** — 특정 게임에 안 묶임(경로·에셋 하드코딩 금지). NightSight/MyProject는 테스트·동기 예시일 뿐.
**안전** — 기본 자산·원본 수정 금지, 쓰기는 백업 우선. (사용자 전역 규칙 준수)

## 라이선스 · 고지
**MIT** (코드·문서에 한함) — `LICENSE` 참조.

이 프로젝트는 **Epic Games와 무관한 독립 도구**이며, 후원·보증받지 않았다.
"Unreal", "UEFN", "Fortnite" 및 관련 자산의 권리는 Epic Games, Inc.에 있다.
**저장소에 Epic 콘텐츠는 포함돼 있지 않다** — 도구는 사용자 머신에 이미 존재하는 파일을 읽을 뿐이다.
사용자가 이 도구로 생성한 데이터(예: 엔진 디바이스 카탈로그)는 Epic 콘텐츠 파생물이므로
이 라이선스가 적용되지 않으며 **재배포해서는 안 된다**. UEFN·Fortnite 사용은 Epic의 ToS/EULA를 따른다.
