# Game Loop Kit (UEFN)

UEFN 게임을 **A-Z 루프 엔지니어링**으로 구축하는 범용 템플릿. `uefn-inspector`를
**구조 센서·검증기 + 부분 액추에이터**로, 기존 uefn/unreal MCP를 **라이브 변경·PIE 검증**으로 쓴다.

이 폴더를 게임 프로젝트 옆에 복사하고 `spec/`·`plan/`을 채운 뒤, LOOP.md 규약대로 루프를 돌린다.

## 구조 = Plan → Task → Ticket
- **Plan**(에픽/마일스톤) → **Task**(하위 묶음) → **Ticket**(루프가 한 번에 실행하는 원자 단위)
- ID = `PLAN.TASK.TICKET` (예 `01.02.03`). 상태 롤업: Ticket → Task → Plan.

## 폴더
```
spec/    무엇/왜 (진실의 원천)      GDD.md · systems/ · assets.md
plan/    무엇을 (계층 작업)          PLANS.md · PLAN-NN/PLAN.md · PLAN-NN/tasks/TASK-*.md
loop/    어떻게 (실행·검증)          LOOP.md · verify/{structural,behavioral}.md · checks/
state/   현재 상태·교훈              SNAPSHOT.md · lessons.md
verse/   게임 Verse 소스
```

## 루프 한 줄
> 티켓 선택 → 구현(Verse+디바이스) → **구조검증(uefn-inspector)** → **행동검증(PIE+로그)** → 통과시 done → 다음.
> 정지게이트에서만 사람 개입. 상세: `loop/LOOP.md`.

## 두 엔진
| | 역할 |
|---|---|
| **uefn-inspector** (오프라인) | 구조 검증 · 선언↔배선 교차검증 · 값/배선 오프라인 쓰기 · SNAPSHOT 생성 |
| **uefn/unreal MCP** (라이브) | 표준 배치 변경 · Verse 컴파일 · **PIE 실행·로그 읽기(행동검증)** |

## 시작
1. `spec/GDD.md`·`spec/systems/`·`spec/assets.md` 작성 (게임 정의)
2. `plan/PLANS.md`에 Plan 추가 → `PLAN-NN/PLAN.md` + `tasks/TASK-*.md`에 Task·Ticket 작성
3. `loop/LOOP.md` 규약으로 루프 실행 (수동 or `/loop`)
4. `state/SNAPSHOT.md`는 uefn-inspector가 자동 갱신, `state/lessons.md`에 교훈 축적
