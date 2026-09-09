# LOOP — 게임 루프 규약

각 반복은 **티켓 하나**를 구조+행동 수용까지 완료한다. 사람은 정지게이트에서만 개입.

## 🔁 한 반복
1. **선택** — `plan/PLANS.md` → 우선 Plan → Task → 맨 위 `todo` 티켓(의존성 충족) → `doing`으로.
2. **설계** — 티켓 수용기준을 보고 필요한 Verse 코드 + 디바이스 배치/배선 결정.
3. **구현**
   - Verse: `verse/<file>.verse` 작성/수정 (AI).
   - 디바이스: 표준 배치·값 = **MCP 라이브** / Verse-VM 값·배선 = **uefn-inspector 오프라인 패치**(에디터 OFF, 백업).
   - **GUI 전용 @editable**(새 슬롯 배선 등)은 → 정지게이트(사람 단계로 표시).
4. **구조검증** (uefn-inspector, 에디터 OFF)
   - 배치·배선·설정이 수용기준과 일치? + **선언↔배선 교차검증**(`.verse` @editable ↔ `.uasset` SavedActor).
   - `loop/verify/structural.md`의 레시피 사용.
5. **행동검증** (라이브 PIE)
   - Verse 컴파일(MCP `BuildAll`) → PIE 실행 → `get_editor_log`/상태로 행동수용 확인.
   - `loop/verify/behavioral.md`의 레시피 사용.
6. **완료** — 둘 다 통과 → 티켓 `done` → Task·Plan 진행률 롤업 → `state/SNAPSHOT.md` 갱신 → 다음 티켓.

## 🛑 정지게이트 (멈추고 사람 호출)
- **GUI 전용 배선** 필요(새 @editable 슬롯을 에디터에서 연결해야 함)
- **행동검증 3회** 실패 → 원인 요약 보고
- **스펙 모호** / 창작 결정 필요
- **파괴적 작업**(원본 덮기·삭제·기본자산 변경) — 승인 우선
- **새 외부 의존성**(에셋·플러그인)

## 상태 값
`todo` · `doing` · `done` · `blocked`(정지게이트 대기)

## 드리프트 검사 (Hybrid C의 상태-diff)
매 반복 or 주기적으로 uefn-inspector로 **현재 상태 ↔ 스펙** 비교:
- 선언됐으나 미배선 @editable (예: 오디오 슬롯) → 새 티켓 or blocked
- 스펙에 없는 배치 / 스펙과 다른 설정값 → 드리프트 티켓
