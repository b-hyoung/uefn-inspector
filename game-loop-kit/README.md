# Game Loop Kit (UEFN)

UEFN 게임을 **A-Z 루프 엔지니어링**으로 구축하는 범용 템플릿. `uefn-inspector`를
**구조 센서·검증기 + 부분 액추에이터**로, 기존 uefn/unreal MCP를 **라이브 변경·PIE 검증**으로 쓴다.

이 폴더를 게임 프로젝트 옆에 복사하고 `spec/`·`plan/`을 채운 뒤, LOOP.md 규약대로 루프를 돌린다.

## 구조 = 재미 가설 → 변주 레벨 → 티켓 (무인 실험 루프)
- **Plan = 재미 가설 1개** → **Task = 변주 레벨 1개** → **Ticket = 그 레벨의 빌드·측정 단위**
- **4레벨 1세트:** A(대조군) · B(**구조**) · C(**규칙**) · D(**인원수**) — 각 레벨은 **한 축만** 변경
- **사람은 루프 안에 없다** — 자동 실행(PIE) + 로그 지표 + 규칙 기반 판정. 사람은 정지게이트에서만.
- ID = `PLAN.TASK.TICKET` (예 `01.02.03`). 롤업: Ticket → Task → Plan → 실험 결론.

## 폴더
```
spec/    무엇/왜 + 재미 가설         INTAKE.md · FUN-HYPOTHESIS.md · GDD.md · systems/ · assets.md
levels/  변주 레벨별 정의·측정        LEVEL-A~D/{build,autoplay,metrics}.md
experiments/ 변주 비교·결론          EXP-NN-results.md
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

## 시작 (순서대로)
1. **`spec/INTAKE.md`** — 질문지대로 캐낸다. *어떤 게임인지 · 재미가 어디서 오는지 · 티켓을 얼마나 잘게 할지.*
2. 답을 **`spec/GDD.md`**(무엇/왜) · **`spec/systems/`**(정확한 규칙) · `spec/assets.md`에 기록
3. **`plan/DECOMPOSE.md`** 규칙으로 Plan→Task→Ticket 배분 → `PLANS.md` · `PLAN-NN/` · `tasks/`
4. **`loop/LOOP.md`** 규약으로 루프 실행 (수동 or `/loop`)
5. `state/SNAPSHOT.md`는 uefn-inspector가 갱신, `state/lessons.md`에 교훈 축적

## 핵심 문서 3개
| 문서 | 답하는 것 |
|---|---|
| **`spec/INTAKE.md`** | **무엇을 물어볼까** — 게임·재미·**깊이(Phase 3.5)**·디테일 수준 질문지 |
| **`spec/FUN-DEPTH.md`** | **얼마나 깊게** — 재미 4층 분해·긴장쌍·실패모드·층별 변주축 |
| **`spec/FUN-HYPOTHESIS.md`** | **무엇이 재미인가** — 가설·자동지표·임계값·판정식 |
| **`plan/DECOMPOSE.md`** | **어떻게 쪼갤까** — 답 → Plan/Task/Ticket 배분 규칙·티켓 크기·수용기준 |
| **`HARNESS.md`** | **뭘 써서 할까** — 사용 가능한 MCP·스킬 목록과 루프 단계별 매핑 |
