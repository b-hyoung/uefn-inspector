# BACKLOG — uefn-inspector

`ROADMAP.md`의 카탈로그를 실행 티켓으로 편 것. 각 티켓의 **수용 테스트가 green이면 완료**.
사람은 매 스텝이 아니라 **티켓 정의 + 마일스톤 + 에스컬레이션**만 본다.

- py: `C:/Users/ACE/AppData/Local/Programs/Python/Python311/python.exe`
- 전체 테스트: `<py> -m pytest -q` (항상 green 유지)
- 픽스처: `tests/fixtures/level/` (audioplayer·wall·classselector) = 미니 프로젝트. 알고리즘은 **합성 데이터 단위테스트** 병행.

## 🔁 루프 규약 (매 반복)
1. 맨 위 `todo` 티켓 → `doing`.
2. TDD: 수용테스트 RED → 최소 GREEN → REFACTOR.
3. `<py> -m pytest -q` 전체 green.
4. 커밋(티켓 ID 포함) → `capability-matrix.md`·이 파일 상태 갱신.
5. 다음 티켓. 정지게이트면 멈추고 보고.

## 🛑 정지게이트
- 설계 모호/스코프 변경 · 매트릭스 **❌ 천장**(Verse-VM 값·@editable 값)은 시도 말고 보고
- 수용테스트 **3회** 실패 시 원인 요약 보고 · **파괴적 작업**(원본 덮기/삭제/기본자산) · 새 외부 의존성

---

## M0 — 기반 견고성

### T1 견고성: 손상/미지원 파일 graceful · `done` · P0
- **수용:** 랜덤 128바이트 임시파일 → `read_package` 예외 없음, `warnings` 있음, `exports==[]`.

### T2 표준 태그드 프로퍼티 디코더 · `deferred` · P1
- **목표:** export serial 영역에서 Bool/Int/Float/Name/Object/Enum 디코드, 모르는 타입 `unparsed`.
- **수용:** `properties.decode(data, pkg, export)` → wall/light에서 표준 프로퍼티 ≥1개 올바른 파이썬 값, 예외 없음. Verse-VM(GUID) 프로퍼티는 `unparsed`.
- **⏸ 재도전 결과(2026-09-09) — 형식 크랙, 정밀구현 대기:**
  - ✅ **태그드 확정**: PackageFlags=0x4840, PKG_UnversionedProperties(0x2000) **unset**. (unversioned 아님)
  - ✅ 버그2개 규명: (a) `FPropertyTag.Size`는 **int32**(export map SerialSize int64와 혼동), (b) 각 export serial 앞에 **선두 1바이트**.
  - ✅ **UE5.4+ `FPropertyTypeName` 형식 확정**: `name(FName8) · type(FName8) · InnerCount(int32) · params(FName8×N) · size(int32) · …` — Struct는 param=구조체명(예 Vector). 옛 walker가 InnerCount 누락해 어긋남.
  - ✅ **실제 디코드 1건 성공**: `CachedMaxDrawDistance FloatProperty=0.0`.
  - ⚠️ 남은 정밀 배치(arrayindex 유무 / Bool 값 위치 / struct GUID / 재귀 중첩)는 probe마다 레이어가 늘어 **엔진 소스 기준 구현 필요**.
  - ❗ "Can Be Heard By"는 **Verse-VM(GUID 낀 커스텀)** = 천장. T2 대상은 표준 컴포넌트 프로퍼티(트랜스폼 등).
  - **다음 열쇠:** UE5.4 `FPropertyTag::Serialize`/`FPropertyTypeName` 엔진 소스 확보 → 정밀 구현. (엔진 소스는 NarshaMCP/UE 설치에 있음)

### T3 트랜스폼 읽기 · `deferred` · P1 (T2 의존)
- **수용:** `inspect_actor(wall)` → `transform.location` 유한 float 3개, 전부 0 아님.
- **⏸ T2 의존이라 함께 보류.**

## M1 — 프로젝트 인덱스 + 검색 (핵심)

### T10 프로젝트 인덱스 · `done` · P0
- **목표:** `index.build_index(dir)` → `{path: Package}` 전 파일 파싱(경고 수집).
- **수용:** level 픽스처 인덱스 → 3개 패키지, 각 `imports`/`exports` 채워짐, 예외 없음.

### T11 참조 그래프 · `done` · P0 (T10)
- **목표:** 파일/패키지 → 참조 대상(import 패키지 경로) 엣지 그래프.
- **수용:** audioplayer 노드가 `Heartbeat_Near`(또는 그 패키지)로 향하는 엣지 보유.

### T12 검색(에셋·디바이스) · `done` · P1 (T10)
- **목표:** `search(index, q)` 이름/클래스/타입 부분일치.
- **수용:** `search(index,"AudioPlayer")` → audioplayer 패키지 포함.

### T13 where-used (역참조) · `done` · P1 (T11)
- **목표:** 주어진 에셋 경로를 참조하는 파일 목록.
- **수용:** `where_used(index,"Heartbeat_Near")` → audioplayer 포함. (지난번 "못 찾던" 것)

### T14 디바이스 설정 발견 · `done` · P1
- **목표:** 패키지의 설정명/enum 타입 나열(값 아님, name표 기반).
- **수용:** audioplayer → `"Can Be Heard By"`와 `"ECreativeAudioPlayerTarget"` 포함.

## M2 — 의존·검증

### T20 순환 의존 탐지 · `done` · P2 (T11)
- **수용:** 합성 그래프(A→B→A)에서 사이클 검출; level 픽스처(비순환)에선 `[]`.

### T21 영향 분석(impact) · `done` · P2 (T11)
- **수용:** `impact(index,"Heartbeat_Near")` → 참조 파일에 audioplayer 포함.

### T22 고아/미사용 에셋 · `done` · P2 (T11)
- **수용:** 합성 인덱스에서 아무도 참조 않는 에셋이 orphan으로, 참조된 것은 제외.

### T23 깨진 참조 탐지 · `done` · P2 (T11)
- **수용:** 프로젝트 내부 대상인데 실재 안 하는 참조만 flag; `/Script`·엔진 참조는 제외.

## M3 — 자산·프로퍼티

### T30 메시 사용 분석 · `done` · P3 (T11)
- **수용:** StaticMesh 참조를 사용하는 액터 매핑 반환(빈 사전 아님).

### T31 머티리얼/텍스처 사용 분석 · `done` · P3 (T11)
- **수용:** Material/MaterialInstance 참조 목록화(픽스처에 존재 시).

### T32 커브(CurveFloat) 분석 · `done` · P3
- **수용:** CurveFloat 참조/에셋 탐지(존재 시 목록, 없으면 빈 결과·예외 없음).

## M4 — 레벨

### T40 레벨 audit/health · `done` · P3 (T10)
- **수용:** 리포트에 디바이스 개수·중복 이름·깨진참조 요약 포함.

### T41 레벨 diff · `done` · P3 (T10)
- **수용:** `diff(levelA, levelA)` == 비어있음; 액터 추가/제거 시 차이 보고.

## M6 — 분석 확장 (NarshaADK 폭 따라잡기, 전부 오프라인 가능)

### T60 hotspot(fan-in 최다 참조) · `done` · P1 (T11)
- **수용:** `hotspots(index)` → (target, count) 내림차순, 최다 참조 자산 1위 반환.
### T61 fan-out(파일별 참조 수) · `done` · P1 (T11)
- **수용:** `fan_out(index)` → {path: 참조수}, audioplayer>0.
### T62 타입 census(클래스 분포) · `done` · P1
- **수용:** `type_census(index)` → Counter, 'BlueprintGeneratedClass' 등 포함.
### T63 외부 의존성 리포트(마운트별) · `done` · P2
- **수용:** `external_deps(index)` → '/Game','/Script' 등 루트별 카운트.
### T64 네이밍 컨벤션 린트 · `done` · P2
- **수용:** `naming_lint(names, rules)` → 규칙 위반 목록(합성 검증).
### T65 문자열/텍스트 추출 · `done` · P2
- **수용:** `extract_strings(pkg)` → 사람이 읽는 문자열(경로 제외) 목록.
### T66 그래프 mermaid 내보내기 · `done` · P2 (T11)
- **수용:** `to_mermaid(index)` → 'graph'로 시작하는 문자열, 엣지 포함.
### T67 의존 깊이/최장 체인 · `done` · P3
- **수용:** `dependency_depth(adj)` → 합성 그래프 최장 경로 길이.
### T68 중복 배치 탐지 · `done` · P3 (T10)
- **수용:** `find_duplicates(index)` → 동일 디바이스 클래스 다중 배치 카운트.
### T69 Verse 디바이스 census · `done` · P3
- **수용:** `verse_devices(index)` → VerseDevice 배치 파일 목록.
### T70 cross-level 에셋 공유 · `done` · P3
- **수용:** 두 레벨 인덱스에서 공유 참조 자산 반환(합성/실).
### T71 파일 크기/bloat 리포트 · `done` · P3
- **수용:** `size_report(index)` → 파일별 바이트, 최대 파일 식별.

## M5 — 노출

### T50 MCP 래핑 · `blocked` · 설계 확정 후
- 분석들을 MCP 도구로 노출. (먼저 라이브러리/CLI 안정화)

## 천장/보류 (루프 대상 아님)
### T7 [BLOCKED] B 쓰기 스파이크 · 사람 승인 필요 (파괴적)
### T8 [보류] 니아가라/시퀀서/DataTable 분석 · 해당 자산 있는 프로젝트 발견 시 개시

---

## 마일스톤 완료 기준
- **M1**: T10~T14 → "찾고·엮는 기반" (지난번 검색 갈증 해소)
- **M2**: T20~T23 → "의존·검증"
- **M3**: T30~T32 (+T2/T3) → "자산·프로퍼티"
- **M4**: T40~T41 → "레벨 감사·비교"
