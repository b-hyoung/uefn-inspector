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
- **⏸ 보류 사유(2026-09-09):** export serial 시작이 단순 FName 태그가 아님(선두 구조/unversioned 직렬화 의심). 3회 탐색 실패 → 규약상 정지. name표엔 타입명 존재(태그드 시사)라 가능성은 있으나 깊은 작업 필요. **M1(찾기) 완료 후 재도전.**

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

### T20 순환 의존 탐지 · `todo` · P2 (T11)
- **수용:** 합성 그래프(A→B→A)에서 사이클 검출; level 픽스처(비순환)에선 `[]`.

### T21 영향 분석(impact) · `todo` · P2 (T11)
- **수용:** `impact(index,"Heartbeat_Near")` → 참조 파일에 audioplayer 포함.

### T22 고아/미사용 에셋 · `todo` · P2 (T11)
- **수용:** 합성 인덱스에서 아무도 참조 않는 에셋이 orphan으로, 참조된 것은 제외.

### T23 깨진 참조 탐지 · `todo` · P2 (T11)
- **수용:** 프로젝트 내부 대상인데 실재 안 하는 참조만 flag; `/Script`·엔진 참조는 제외.

## M3 — 자산·프로퍼티

### T30 메시 사용 분석 · `todo` · P3 (T11)
- **수용:** StaticMesh 참조를 사용하는 액터 매핑 반환(빈 사전 아님).

### T31 머티리얼/텍스처 사용 분석 · `todo` · P3 (T11)
- **수용:** Material/MaterialInstance 참조 목록화(픽스처에 존재 시).

### T32 커브(CurveFloat) 분석 · `todo` · P3
- **수용:** CurveFloat 참조/에셋 탐지(존재 시 목록, 없으면 빈 결과·예외 없음).

## M4 — 레벨

### T40 레벨 audit/health · `todo` · P3 (T10)
- **수용:** 리포트에 디바이스 개수·중복 이름·깨진참조 요약 포함.

### T41 레벨 diff · `todo` · P3 (T10)
- **수용:** `diff(levelA, levelA)` == 비어있음; 액터 추가/제거 시 차이 보고.

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
