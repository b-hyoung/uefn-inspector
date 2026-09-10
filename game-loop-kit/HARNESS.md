# HARNESS — 이 kit이 쓰는 MCP·스킬 목록 (실측 2026-09-10)

루프 각 단계에서 **무엇을 호출해 쓰는지**의 색인. 없는 건 안 쓴다.

## 1. MCP 서버 (등록됨)
| 서버 | 종류 | 루프에서의 역할 |
|---|---|---|
| **uefn-inspector** | stdio(우리 도구) | **오프라인 전담** — 아래 §1.5 표가 핵심 |
| **uefn** (KirChuvakov) | stdio → UEFN 리스너 | **라이브 조작**·`execute_python`(임의 unreal)·`get_editor_log`(**행동검증**)·액터/에셋/뷰포트 |
| **unreal-mcp** (Epic 공식) | http :8000 | UEFN 내장 MCP — Verse 컴파일(BuildAll)·고정 툴셋 (에디터 ON 필요) |
| git | stdio | 커밋·이력 (티켓 단위 커밋) |
| sqlite · n8n · blender · unrealclaude | — | 이 kit 범위 밖(다른 작업용) |

## 1.5 ⭐ 오프라인으로 되는 것 (= 이 도구를 쓰는 이유)

> **핵심:** 아래 ⭐ 항목들은 **라이브 MCP·에디터 Python 리플렉션이 못 한다.**
> "GUI로만 가능"이라고 판단하기 전에 **반드시 이 표를 본다.** (2026-09-10 실측·UEFN 수용 검증됨)

| 하려는 것 | MCP 도구 / 라이브러리 | 라이브(uefn/unreal-mcp) | 오프라인(uefn-inspector) |
|---|---|---|---|
| ⭐ **`@editable` 배선 읽기** (어느 슬롯이 뭐에 연결됐나) | `editable_bindings` · `analysis.verse.verse_bindings` | ❌ 못 읽음(Verse VM 내부) | **✅ 읽힘** |
| ⭐ **`@editable` 배선 변경**(기존 슬롯 재연결) | `edit.write.set_object_ref` | ❌ | **✅ 씀** (UEFN 수용 확인) |
| ⭐ **디바이스 설정값 읽기**(예 `Can Be Heard By`) | `read_actor` · `core.properties.decode_properties` | ❌ | **✅ 읽힘** |
| ⭐ **디바이스 설정값 변경**(enum) | `edit.write.set_enum` | ❌ | **✅ 씀** |
| ⭐ **선언↔배선 교차검증**(미배선 슬롯 탐지) | `analysis.verse_source.cross_reference` | ❌ | **✅** (스펙 드리프트 자동 감지) |
| 프로퍼티 값·트랜스폼 | `read_actor` | 표준값만 △ | ✅ (91% 디코드) |
| 스칼라 값 변경 | `edit.write.set_scalar` · `edit.patch.patch_scalar_file`(백업+롤백) | 표준값 ✅ | ✅ (에디터 닫고) |
| 레벨 인벤토리·검색·역참조·의존/영향 | `inspect_level`·`find`·`who_uses`·`audit` | 크로스파일 ❌ | ✅ |
| 공간 분석(bounds·밀집·간격) | `analysis.spatial.*` | ❌ | ✅ |
| 엔진 디바이스 카탈로그 | `engine_devices` | ❌ | ✅ (로컬 생성 시) |

**대신 오프라인이 못 하는 것 (라이브 몫)**
- 게임 **실행**(PIE)·런타임 상태·로그 → `uefn`
- Verse **컴파일** → `unreal-mcp` BuildAll
- **새 `@editable` 슬롯 배선 추가**(없던 걸 새로 잇기) → GUI (크기변경 쓰기 미구현)

**운영 규칙**
- 오프라인 **쓰기**는 **UEFN을 닫고** 한다(에디터가 파일을 잠금). 읽기는 켜져 있어도 됨.
- 표준 배치·트랜스폼만 바꿀 거면 굳이 닫지 말고 **라이브 MCP**로.
- Verse-VM 값·배선을 바꿀 땐 **닫은 김에 다른 오프라인 작업까지 몰아서** 한 번에.

## 2. 게임 설계 하네스 — `game-design-skill` (v0.3.0)
> 출처: Claude Code Game Studios(MIT) 자료. **INTAKE/GDD/시스템 문서의 근거.**

**워크플로(질문·절차)**
`brainstorm`(인테이크 뼈대) · `map-systems`(컨셉→시스템 분해) · `design-system`(시스템 GDD 작성)
`quick-design`(소규모 변경) · `design-review` · `review-all-gdds` · `consistency-check`
`balance-check` · `scope-check` · `content-audit` · `propagate-design-change`
`prototype` · `playtest-report` · `ux-design` · `ux-review`

**템플릿(문서 뼈대)**
`game-concept` · `game-pillars` · `player-journey` · `systems-index` · `game-design-document`
`economy-model` · `difficulty-curve` · `prototype-report` · `ux-spec` · `hud-design`
`interaction-pattern-library` · `level-design-document` · `accessibility-requirements`

**전문 에이전트 렌즈**
`game-designer` · `systems-designer` · `creative-director` · `economy-designer`
`level-designer` · `ux-designer` · `accessibility-specialist` · `prototyper` · `live-ops-designer`

**규칙/출처**
`rule-design-docs` · `authoritative-sources`(MDA·SDT·Bartle 등 인용 기준) · `provenance`

## 3. AI 네이티브 게임 설계 — `ai-native-game-design` (v0.2.0)
`ai-native-game-design.md` · `ai-npc-design.md` — 런타임 AI가 개입하는 메카닉 설계 시 참조.

## 4. UE 분석 하네스 — `narsha-adk` (v0.9.12, 40 스킬)
> **주의:** 대부분 **UE C++/에디터 라이브** 전제라 UEFN에는 그대로 안 맞는다.
> **개념 참고용**으로만: `ue-audit`·`ue-impact`·`ue-asset-discovery`·`ue-diff`·`ue-validate`·
> `ue-plan-review`·`game-design-intelligence`. (UEFN 실행은 uefn-inspector로 대체)

## 5. 프로세스 하네스 — `superpowers` (v5.0.7)
`brainstorming`(설계 전 요구 정리) · `writing-plans` · `executing-plans` ·
`test-driven-development` · `systematic-debugging` · `requesting-code-review` ·
`verification-before-completion` · `dispatching-parallel-agents`
→ **티켓 실행 규율**(TDD·검증)과 계획 수립에 사용.

## 6. 기타
- `elements-of-style` — 문서 문장 다듬기 (GDD/티켓 가독성)
- `impeccable` — UI/시각 결과물 필요 시
- `mattpocock-skills` — `diagnosing-bugs`·`tdd`·`domain-modeling`·`grilling`(설계 압박테스트)

---

## 루프 단계 ↔ 하네스 매핑
| 단계 | 쓰는 것 |
|---|---|
| **spec 채우기(인테이크)** | game-design-skill `workflow-brainstorm` + `template-game-concept/pillars` → `spec/INTAKE.md` |
| **시스템 분해** | `workflow-map-systems` → `spec/systems/` + `template-systems-index` |
| **시스템 규칙 작성** | `workflow-design-system` + `template-game-design-document` |
| **티켓 배분** | `DECOMPOSE.md`(이 kit) + superpowers `writing-plans` |
| **구현** | uefn MCP(라이브) · uefn-inspector(오프라인 쓰기) · superpowers `TDD` |
| **구조검증** | **uefn-inspector** (`loop/verify/structural.md`) |
| **행동검증** | uefn `get_editor_log`+PIE · unreal-mcp BuildAll (`loop/verify/behavioral.md`) |
| **밸런스·스코프 점검** | `workflow-balance-check` · `workflow-scope-check` |
| **플레이테스트 반영** | `workflow-playtest-report` → `state/lessons.md` |
| **설계 변경 전파** | `workflow-propagate-design-change` + `consistency-check` |
