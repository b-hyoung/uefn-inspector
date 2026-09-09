# HARNESS — 이 kit이 쓰는 MCP·스킬 목록 (실측 2026-09-10)

루프 각 단계에서 **무엇을 호출해 쓰는지**의 색인. 없는 건 안 쓴다.

## 1. MCP 서버 (등록됨)
| 서버 | 종류 | 루프에서의 역할 |
|---|---|---|
| **uefn-inspector** | stdio(우리 도구) | **구조검증**·오프라인 읽기/쓰기·선언↔배선 교차검증 (`inspect_level`·`read_actor`·`editable_bindings`·`find`·`who_uses`·`audit`·`engine_devices`) |
| **uefn** (KirChuvakov) | stdio → UEFN 리스너 | **라이브 조작**·`execute_python`(임의 unreal)·`get_editor_log`(**행동검증**)·액터/에셋/뷰포트 |
| **unreal-mcp** (Epic 공식) | http :8000 | UEFN 내장 MCP — Verse 컴파일(BuildAll)·고정 툴셋 (에디터 ON 필요) |
| git | stdio | 커밋·이력 (티켓 단위 커밋) |
| sqlite · n8n · blender · unrealclaude | — | 이 kit 범위 밖(다른 작업용) |

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
