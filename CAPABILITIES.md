# CAPABILITIES — 되는 것 / 안 되는 것 (확정 분류)

> 루프(M1~M4) 완료 시점의 확정 능력표. 실제 MyProject/PointLevel(67 액터)로 검증.
> 도구는 **범용**(어떤 UEFN 프로젝트든). NightSight는 테스트 대상일 뿐.
> 최종: 2026-09-09 · 테스트 24 green

범례: ✅ 검증됨 · ⚠️ 부분/조건부 · ❌ 불가(천장) · ⏸ 보류

---

## A. 읽기 · 오프라인 (에디터 OFF) — ✅ 되는 것

| 능력 | 함수 | 실증 |
|---|---|---|
| 패키지 파싱(헤더/Name/Import/Export+serial) | `read_package` | AudioPlayer 등 실파일 |
| 손상/짧은 파일 graceful | `read_package` | 크래시 대신 warnings |
| 레벨 인벤토리(디바이스·에셋) | `inspect_level` | 67액터·9종 |
| CLI 리포트(사람/JSON) | `python -m uefn_inspector` | 동작 |
| 프로젝트 인덱스 | `build_index` | 67패키지 |
| 참조 그래프(누가 누구를) | `build_reference_graph` | forward+reverse |
| **검색**(이름/클래스/타입) | `search` | 'Wall'→46 |
| **where-used**(역참조) | `where_used` | Heartbeat_Near→1 |
| 디바이스 **설정 발견**(이름·enum) | `list_settings` | 'Can Be Heard By'+enum |
| 순환 의존 탐지 | `find_cycles` | 합성 검증 |
| 영향 분석(X 바꾸면?) | `impact` | Heartbeat→1파일 |
| 고아/미사용 | `find_orphans` | 합성 검증 |
| 깨진 참조 | `find_broken_refs` | 합성 검증 |
| 커브 사용 | `curve_usage` | 실 1건 |
| 레벨 audit(개수·중복·경고) | `audit_level` | 9종·중복7 |
| 레벨 diff(버전 비교) | `diff_levels` | 동일=∅ |
| **hotspot(fan-in 최다참조)** | `hotspots` | Wall 46, ToyOptions 13 |
| **fan-out(파일별 참조수)** | `fan_out` | ✅ |
| **타입 census(클래스 분포)** | `type_census` | Package347·Class294·BPGC129 |
| **외부 의존성(마운트별)** | `external_deps` | /Script1253·/Game101·/CRD_… |
| **네이밍 컨벤션 린트** | `naming_lint` | 합성 검증 |
| **문자열/텍스트 추출** | `extract_strings` | 'Can Be Heard By' 등 |
| **그래프 mermaid 내보내기** | `to_mermaid` | graph LR + 엣지 |
| **의존 깊이/최장 체인** | `dependency_depth` | 합성 검증 |
| **중복 배치 탐지** | `find_duplicates` | 6종 |
| **Verse 디바이스 census** | `verse_devices` | 2개 |
| **cross-level 에셋 공유** | `cross_level_shared` | 합성 검증 |
| **파일 크기/bloat** | `size_report` | 총 621KB, 최대 53KB |
| **컴포넌트 구성**(디바이스별) | `component_composition` | AudioPlayer 18컴포넌트 |
| **outer 컨테인먼트 트리** | `outer_tree` | 액터→컴포넌트 |
| **soft/hard 참조 분리** | `soft_hard_refs` | hard6·soft5 |
| **아키텍처 린트**(컴포넌트 과다) | `arch_lint` | 임계 초과 파일 |
| **actor 단위 diff**(이름) | `actor_diff` | added/removed |
| **transitive 도달**(의존 확장) | `transitive_reachable` | 합성 |
| **DOT 그래프 내보내기** | `to_dot` | Graphviz |
| **엔진 버전 census** | `engine_version_census` | 522/1018 |
| **GameplayTag census(휴리스틱)** | `gameplay_tag_census` | 점표기 식별 |

## B. 읽기 · 오프라인 — ⚠️ 조건부

| 능력 | 상태 | 조건 |
|---|---|---|
| 메시/머티리얼 사용 | ⚠️ 함수 OK, **입력 필요** | 배치 액터는 메시를 BP 통해 *간접* 참조 → 콘텐츠 에셋(.uasset)까지 인덱싱해야 잡힘. 액터만으론 0 |
| 깨진 참조(실프로젝트) | ⚠️ | 전체 에셋 인덱스 필요(액터만으론 판정 어려움) |

## C. 읽기 · 오프라인 — ⏸ 보류 / ❌ 천장

| 능력 | 상태 | 사유 |
|---|---|---|
| 표준 프로퍼티 **값**(Bool/Int/Float/Enum) | ⏸ 보류(T2) | export serial이 단순 태그드 아님(선두구조/unversioned 의심). 깊은 작업 필요 |
| 트랜스폼 값 | ⏸ 보류(T3) | T2 의존 |
| 디바이스 설정 **값**(`Can Be Heard By`=?) | ❌ 천장 | GUID 낀 Verse-VM 직렬화. 이름은 보여도 값은 못 읽음 |
| `@editable` 바인딩 **값** | ❌ 천장 | Verse VM 내부(리플렉션도 실패). 라이브 GUI만 |
| 니아가라/시퀀서/DataTable | ⏸ | 이 프로젝트에 부재. 있는 프로젝트 발견 시 개시 |

---

## D. 수정(쓰기) · 오프라인 — 조사 결과 (사본 검증, 원본 불변)

| 능력 | 상태 | 근거 |
|---|---|---|
| 라운드트립(무변경 재기록) | ✅ | 바이트 동일 |
| **동일 길이 in-place 치환**(참조 리다이렉트 등) | ⚠️ 구조상 OK | 사본에서 파싱 온전. 오프셋 안 밀림 |
| 다른 길이 치환 | ❌ | 오프셋 깨짐 → fixup 엔진 필요(미구현) |
| 이름 해시 재계산 / UEFN 수용 | ❓ 미검증 | 동일길이라도 name 해시가 옛 값 → UEFN 로드/퍼블리시 수용 **미확인**. 실검증=파괴적(사람 승인) |
| Verse-VM 값·@editable 쓰기 | ❌ 천장 | 라이브도 불가한 영역 |

**요약:** 오프라인 쓰기는 "**동일 길이 in-place 패치**"까지 구조적으로 가능(참조 스왑 등). 그 이상(길이변경·추가·삭제)은 오프셋 fixup 엔진이 있어야 하고, **실제 UEFN 수용은 미검증**(T7, 파괴적이라 사람 승인 필요).

---

## E. 온라인(에디터 ON) — 기존 MCP 대비 내 위치

**기존 MCP가 하는 것**
- 공식 `unreal-mcp`(:8000, 고정 툴셋): 액터 스폰, 표준 프로퍼티, 머티리얼, 테스트, Verse 컴파일.
- 커뮤니티 `uefn`(`execute_python`): 에디터 안 **임의 Python** — 매우 강력.
- 공통: **에디터가 켜져 있어야** 함. **크로스파일/오프라인 관점 없음.**

**내가 추가하는 것 (기존 MCP가 못 함)**
- ✅ **에디터 OFF** 전 분석(A 전체) — MCP 불가
- ✅ **프로젝트 전체 그래프**(where-used/영향/고아/깨진참조/diff) — MCP는 라이브 단일객체 조회라 크로스파일 없음
- ✅ **버전 diff / 배치·병렬** — MCP 불가
- ✅ **하이브리드**: 오프라인 그래프로 "무엇을 바꿀지" 판단 → 적용은 `execute_python`으로 (MCP 단독 불가)
- ✅ **디스크 .uasset 동일길이 패치** → 에디터 reload (MCP는 파일 안 만짐)

**아무도 못 하는 것 (온·오프 공통 천장)**
- ❌ Verse-VM `@editable`·디바이스 설정 **값** 읽기/쓰기 — 온라인 `execute_python`도 실패 확인. 라이브 **GUI 수동**만.

**정직한 결론:** 순수 온라인 조작은 `execute_python`이 이미 대부분 커버. 내 진짜 보완가치는 **오프라인 분석 + 하이브리드(오프라인 판단→온라인 실행)**, 그리고 **파일 디스크 패치**. Verse-VM 천장은 온·오프 모두 동일.

---

## 🧱 확장 한계 — "더 못 채우는 이유" (현재 모델 = 배치 액터/레벨 uasset, 값 미디코드)

지금 모델로 오프라인 분석은 **~38개까지 채웠고**, 그 이상은 아래 셋 중 하나를 뚫어야 가능:

1. **프로퍼티 값 디코드(T2)** — 잠기면: 트랜스폼/공간배치, 실제 수치·설정값, 스칼라 프로퍼티 분석.
2. **콘텐츠 에셋 인덱싱**(BP/메시/머티리얼 .uasset, 배치 액터 아님) — 잠기면: 클래스 계층(super_index는 인스턴스라 0), 실 메시/머티리얼 사용, 완전한 의존 해소.
3. **라이브 에디터** — 잠기면: Verse-VM `@editable`·설정 **값** (온·오프 공통 천장, GUI만).

즉 "분석 종류"는 사실상 소진. 남은 건 **깊이(값)·범위(콘텐츠 에셋)·런타임(라이브)** 축의 확장이며, 각각 위 3개 열쇠가 필요하다.

## 한 장 요약
- **읽기/분석**: 오프라인으로 폭넓게 ✅ (검색·역참조·의존·감사·diff)
- **프로퍼티 값**: 표준값 ⏸보류 · Verse-VM값 ❌천장
- **쓰기**: 오프라인 동일길이 패치 ⚠️(수용 미검증) · 그 이상은 미구현/천장
- **온라인**: 기존 MCP 못하는 오프라인·크로스파일·하이브리드가 내 몫. Verse-VM은 GUI만.
