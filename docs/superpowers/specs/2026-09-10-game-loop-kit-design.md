# Game Loop Kit — 설계 (Spec)

- 날짜: 2026-09-10 · 상태: 승인됨(brainstorming 완료)
- 위치: `uefn-inspector/game-loop-kit/` (범용 템플릿 — 게임 프로젝트에 복사해 사용)

## 목적
uefn-inspector를 **구조 센서·검증기 + 부분 액추에이터**로 삼아, UEFN 게임을
**A-Z 루프 엔지니어링**으로 구축한다. 사람이 매 스텝 확인하지 않고, 정지게이트에서만 개입.

## 결정 (brainstorming)
- **범위:** 범용 템플릿 (게임 무관, 재사용). 구체 내용은 사용자가 채움.
- **루프 구동:** Hybrid C — **티켓이 "무엇을 만들지"**, **상태-diff가 "스펙대로/드리프트"**(예: `.verse` 선언 @editable ↔ `.uasset` 실제 배선 불일치 = HeartMid류 자동 감지).
- **검증:** 구조(uefn-inspector, 에디터 OFF) + 행동(라이브 PIE: MCP BuildAll→PIE→get_editor_log).
- **구조화:** **Plan → Task → Ticket** 3계층. Task 파일 안에 여러 Ticket. ID = `PLAN.TASK.TICKET`(예 01.02.03).

## 계층
- **Plan** = 에픽/마일스톤 (무엇·왜). 폴더 `PLAN-NN/` + `PLAN.md`.
- **Task** = 하위 묶음. 파일 `tasks/TASK-NN.MM.md` — 그 안에 Ticket들.
- **Ticket** = 루프의 원자 실행 단위. 구조수용 + 행동수용 + status(todo/doing/done/blocked) + deps.

## 폴더 구조
```
game-loop-kit/
├── README.md
├── spec/     GDD.md · systems/ · assets.md         (진실의 원천)
├── plan/     PLANS.md · PLAN-NN/PLAN.md · PLAN-NN/tasks/TASK-*.md
├── loop/     LOOP.md · verify/{structural,behavioral}.md · checks/
├── state/    SNAPSHOT.md · lessons.md
└── verse/    게임 Verse 소스
```

## 루프 규약 (LOOP.md)
1. PLANS.md → 우선 plan → task → 맨 위 `todo` 티켓(의존성 충족) 선택 → `doing`
2. 설계 → Verse 코드 + 디바이스 배치/배선 결정
3. 구현 → `.verse` 작성(AI) + 디바이스(MCP 라이브 / uefn-inspector 오프라인 패치, GUI전용 @editable은 사람 단계 표시)
4. **구조검증** — uefn-inspector: 배치·배선·설정 = 스펙? + 선언↔배선 교차검증
5. **행동검증** — Verse 컴파일→PIE→로그/상태 확인 = 행동수용?
6. 둘 다 통과 → `done` → task·plan 진행률 롤업 → SNAPSHOT 갱신 → 다음
- **정지게이트:** GUI전용 배선 필요 / 행동 N회(3) 실패 / 스펙 모호 / 파괴적 / 새 의존성

## 두 엔진 역할
- **uefn-inspector:** 구조 검증(오프라인) · 값/배선 오프라인 쓰기 · 선언↔배선 교차검증 · SNAPSHOT 생성
- **uefn/unreal MCP:** 라이브 배치 변경 · PIE 실행·로그 읽기(행동검증)

## 비목표
- 게임별 구체 콘텐츠(템플릿은 플레이스홀더) · Verse 코드 "의미" 자동생성(사람/AI가 스펙 기반 작성) · 크기변경 대량 리라이트(uefn-inspector fixup 엔진 성숙 후)
