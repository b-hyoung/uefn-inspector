# CHANGELOG

`git pull` 후 **무엇이 바뀌었는지** 확인하는 곳. 새 기능·깨지는 변경·해제된 한계를 기록한다.

형식: [Keep a Changelog](https://keepachangelog.com/) 느슨한 적용 · 날짜는 YYYY-MM-DD.
`Added`(새 기능) · `Changed`(동작 변경) · `Fixed`(버그) · `Unlocked`(불가→가능) ·
`Breaking`(호환 깨짐) · `Docs`(문서/규율).

---

## [Unreleased]

### Unlocked
- **새 `@editable` 슬롯 배선 추가** — `edit.add_binding.add_binding(file, slot, template_slot)`.
  기존 슬롯 *변경*(`set_object_ref`)에 이어, **없던 슬롯을 새로 잇는 것**까지 오프라인으로 가능.
  기존 `__verse_` export를 템플릿으로 복제 → 이름·export 추가 → 모든 오프셋 fixup → 자동 검증·롤백.
  실증: versedevice에 `HeartMid` 추가 (exports 11→12, 기존 배선 3개 온전).
  ⚠️ **UEFN 수용 미검증**(크기변경 편집). 사본으로 시험하고 `.bak` 유지할 것.

### Added
- `edit/rebuild.py` `trailing_offsets()` — 요약의 후행 오프셋(depends·asset-registry·bulk-data) 발견,
  크기변경 시 삽입 지점 이후 값만 이동시키는 fixup.
- `core/uasset.py` `Package.name_count_pos` — 요약 필드 위치를 리더가 보관(쓰기 측 추측 제거).
- 설치 CLI `bin/cli.js` — `install` / `skills` / `mcp` / `doctor` / `uninstall`.
  Python 3.11+ 자동 탐지(`UEFN_PYTHON` 오버라이드), `mcp` 패키지 자동 설치, `claude mcp add` 자동 실행.
- `package.json` — npm 배포 준비(`npx uefn-inspector install`).

### Fixed
- 새 클론에서 픽스처 없이 45개 테스트가 **실패**하던 것 → 자동 **skip**(conftest). 클론 직후 오해 방지.
- name 삽입 지점을 `import_offset`으로 잡아 그 사이 블록(gatherable text 등)을 깨뜨리던 버그 →
  **name 표를 실제로 걸어서** 끝을 찾도록 수정.

### Docs
- `game-loop-kit/HARNESS.md` §1.5 **오프라인으로 되는 것** 표 — 라이브 MCP가 못 하는 것과 대비.
- HARNESS 상단 **"안 되는 걸 된다고 하지 마라"** 규율 5개(미검증 표기·실행으로 확인·환경 조건 구분·
  실패는 실패로·틀리면 즉시 수정) → 잘못된 역량 주장 = 실험 결과 무효(리뷰 Blocker).
- `/uefn-game-loop` 절대규칙 7번, `/uefn-review` **B-6 역량 주장 공격** 추가.
- `spec/UEFN-FEASIBILITY.md` **0단계 — 게임 형태 적합성**(2D·턴제·RTS 등)과 UEFN식 번역.

---

## [0.1.0] — 2026-09-10

첫 공개. UEFN `.uasset/.umap`를 **에디터 없이** 읽고 고치는 도구 + 게임 루프 프레임워크.

### Added — 분석 (오프라인)
- `.uasset/.umap` 파서: name·import·export(serial 영역), 손상 파일 graceful.
- 프로퍼티 값 디코드(UE5.4 `FPropertyTypeName`): Float/Int/Bool/Str/Enum/Object/Struct — **91%**.
- 프로젝트 인덱스·참조 그래프, 검색·where-used·설정 발견.
- 의존 분석: 순환·영향·고아·깨진참조 · hotspot·fan-out·의존깊이 · mermaid/DOT 내보내기.
- census: 타입·외부의존·엔진버전·GameplayTag · 네이밍 린트 · 문자열 추출 · 크기 리포트.
- 구조: 컴포넌트 구성·outer 트리·soft/hard 참조·아키텍처 린트.
- 공간: bounds·density·min-spacing (트랜스폼 디코드 기반).
- `.verse` 소스 분석 + **선언↔배선 교차검증**(미배선 슬롯 자동 탐지).
- 레벨 audit·diff·actor diff, CLI(`python -m uefn_inspector <경로>` / `--json`).

### Added — 편집 (오프라인, 동일 크기)
- `set_scalar`·`set_enum`·`set_object_ref` + 백업·롤백 파일 패치(`patch.py`).

### Unlocked — 라이브 MCP가 못 하던 것
- **Verse-VM 디바이스 설정값** 읽기·쓰기 (예: `Can Be Heard By`).
- **`@editable` 배선** 읽기·변경. **UEFN 수용 라이브 검증 완료**(벽 Z 이동 + knife_sense 재배선).

### Added — 인터페이스
- MCP 서버 7도구: `inspect_level`·`audit`·`find`·`who_uses`·`read_actor`·`editable_bindings`·`engine_devices`.
- 슬래시 스킬 4종: `/uefn-game-loop`(루프 실행자) · `/uefn-intake` · `/uefn-level` · `/uefn-review`.

### Added — game-loop-kit
- 무인 실험 루프: ①인테이크 → ②DOR → ③분해 → ④레벨×4(구조/규칙/인원) → ⑤규칙 기반 판정 → 복귀.
- INTAKE(질문지)·GENRE-PACKS(7장르)·FUN-DEPTH(4층·긴장·실패)·FUN-HYPOTHESIS(지표·판정식)·
  DECOMPOSE·DOR·TIMEBOX(3시간)·ADVERSARIAL(판단 가능성 공격)·UEFN-FEASIBILITY.

### Added — 엔진 콘텐츠
- CUE4Parse CLI 가이드(`cue4parse_cli/README.md`) — Fortnite paks 마운트 → 디바이스 카탈로그 생성.
  카탈로그 자체는 **배포하지 않음**(Epic 파생물).

### 알려진 한계
- **usmap 없이는** 엔진 에셋의 프로퍼티 값·클래스 계층 불가(외부 소스 의존).
- 크기변경 편집의 **UEFN 수용 미검증**(동일 크기는 검증됨).
- Verse 코드의 *의미* 해석은 범위 밖.
