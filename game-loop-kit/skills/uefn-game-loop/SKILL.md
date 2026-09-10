---
name: uefn-game-loop
description: Use when building or testing a UEFN game with the game-loop-kit — running the intake (what game / where the fun is / genre pack), decomposing into Plan→Task→Ticket, building 4 variation levels (structure/rules/player-count), verifying offline with uefn-inspector, running the unattended experiment loop, or adversarially reviewing whether the game's fun is judgeable. Triggers on "게임 루프", "재미 검증", "레벨 변주", "인테이크", "적대적 리뷰", "game loop kit", UEFN game design/測定 requests.
---

# UEFN Game Loop

UEFN 게임을 **무인 실험 루프**로 만든다: 재미 가설 하나 → 4개 변주 레벨 → 자동 측정 → 규칙 기반 판정.

**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit`
(GitHub: b-hyoung/uefn-inspector · 게임 프로젝트에 복사해 쓰는 범용 템플릿)

## 무엇부터 할지 (사용자 요청 → 진입점)

| 요청 | 읽을 문서 | 하는 일 |
|---|---|---|
| "이런 게임 만들래" / 기획 시작 | `spec/INTAKE.md` + `spec/GENRE-PACKS.md` | 인테이크 질문 (사람→컨셉→**장르팩**→루프→**깊이파기**) |
| "재미를 더 깊게" | `spec/FUN-DEPTH.md` | 4층 분해·긴장쌍·실패모드 |
| "가설·지표 정하자" | `spec/FUN-HYPOTHESIS.md` | 자동지표·임계값·판정식·반증조건 |
| "작업 쪼개줘" | `plan/DECOMPOSE.md` | Plan(가설)→Task(레벨)→Ticket |
| "레벨 만들자" | `loop/LOOP.md` + `loop/TIMEBOX.md` | 티켓 루프 (3시간 예산) |
| "검증해줘" | `loop/verify/{structural,behavioral}.md` | 구조(오프라인)+행동(PIE) |
| "리뷰해줘" / 꼼꼼히 | `loop/review/ADVERSARIAL.md` | **재미를 판단할 수 있나** 공격 |
| "시작해도 돼?" | `spec/DOR.md` | 착수 게이트 |
| 뭘 쓸 수 있나 | `HARNESS.md` | MCP·스킬 목록 |

## 절대 규칙 (이 kit의 정체성)

1. **판단 가능성이 최우선** — "재미있나"보다 **"재미를 판단할 수 있나"**.
   정의·관측·구별·반증 4조건 중 하나라도 거짓이면 만들기를 멈추고 그것부터 고친다.
2. **사람은 루프 안에 없다** — 자동 실행(PIE) + 로그 지표 + 규칙 기반 판정.
   사람은 **정지게이트에서만** 부른다. 주관 평가·플레이테스트를 루프에 넣지 않는다.
3. **한 레벨 = 한 축만 변경** — A(대조) · B(구조) · C(규칙) · D(인원). 둘 이상 바꾸면 인과 불가.
4. **장르는 답이 아니라 질문의 안내자** — 관습 수치("슈터니까 TTK 3초")를 값으로 가정하지 않는다.
5. **표층만 있으면 반려** — 감각만 있고 판단·숙련이 없으면 그 재미는 얕다(FUN-DEPTH 4층 중 3층 이상).
6. **측정은 절대 못 뺀다** — 시간이 모자라면 다른 걸 컷한다. 측정 없으면 그 레벨은 무효.

## 실행 도구 (HARNESS.md 상세)
- **uefn-inspector** MCP — 구조검증·오프라인 읽기/쓰기·선언↔배선 교차검증
  (`inspect_level`·`read_actor`·`editable_bindings`·`find`·`who_uses`·`audit`·`engine_devices`)
- **uefn** MCP — 라이브 조작·`execute_python`·`get_editor_log`(행동검증)
- **unreal-mcp** — Verse 컴파일(BuildAll)
- 설계 렌즈: `game-design-skill` 워크플로/템플릿 · `mattpocock-skills:grilling`(전면 공격)

## 흔한 함정
- **자동 구동 모드 부재** → 무인 루프의 급소. A레벨에서 먼저 구축(없으면 루프가 못 돈다).
- **GUI 전용 @editable 배선** → 사람 대기. 발견 즉시 정지게이트·별도 티켓.
- **오프라인 쓰기 = UEFN 닫아야 함**(파일 잠금). 표준값은 라이브 MCP로.
- **굿하트 오염** — 지표를 만족시키면서 재미없게 노는 법이 있으면 지표를 바꾼다.

## 진행 원칙
- 인테이크는 **한 번에 하나씩** 대화로. 체크리스트 낭독 금지.
- 답이 **설계를 바꾸는 질문만** 한다. 뻔한 건 기본값으로 정하고 통보.
- 각 단계 산출물은 kit의 해당 파일에 기록한다(문서가 곧 상태).
