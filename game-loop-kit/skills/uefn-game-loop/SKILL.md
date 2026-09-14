---
name: uefn-game-loop
description: Run the whole UEFN game loop end-to-end — intake (what game / where the fun is / genre pack / depth), readiness gate, decomposition into Plan→Task→Ticket, building 4 variation levels (structure/rules/player-count) inside a 3-hour timebox with offline structural verification and PIE behavioral verification, adversarial review at every ticket, and rule-based judgement of the fun hypothesis. Use for any UEFN game build/test/measure request; the other uefn-* skills are shortcuts into single stages of this loop.
---

# UEFN Game Loop — 루프 실행자

기본 진입점. `/uefn-intake`·`/uefn-level`·`/uefn-review`는 중간 진입용 단축키다.
**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit` · 규약 원본 `KIT/loop/LOOP.md`

## 규칙 0 — 루프 무정지 (최상위, 아래 모든 규칙에 우선)
- 경계는 ② DOR 통과다. 그 이전(①·②)에는 질문한다. 통과 이후 ⑤ 판정 보고까지는 **사람에게 묻지 않고 멈추지 않는다.**
- 막히면 `state/deferred.md`에 한 건 기록(무엇·왜·택한 가정·영향 범위) 후 가장 보수적인 가정으로 진행한다. 진행 불가 티켓은 `deferred`로 표시하고 다음 티켓으로 간다.
- 파괴적 작업(원본 덮기·삭제·기본자산 변경)과 새 외부 의존성 설치는 실행하지 않고 deferred로 기록한 뒤 우회한다.
- 행동검증 3회 실패는 해당 레벨을 `무효`로 표시하고 다음 레벨로 간다. GUI 전용으로 보이는 작업은 `capabilities` 확인 후에만 deferred로 둔다.
- 종료 후 보고 순서: 결과 → deferred 목록(우선순위·가정·되돌리는 법) → 질문. 질문은 이때 한 번에 한다.
- 환경 장애(로그아웃 `Play command not available`·런처 재기동·프리즈·MCP 도구 소실)는 `loop/recover.md`대로 자동 복구한다. 조기 종료는 하드 실패(같은 복구 절차 2회 연속 실패, 4레벨 타임박스 소진)뿐이며, 그 경우도 질문이 아니라 종료 보고다.

## THE LOOP
```
①인테이크 → ②DOR게이트 → ③분해 → ④레벨×4 → ⑤판정 → (기각/애매/무효 시 해당 지점으로 복귀)
```

### ① 인테이크 = 기획 루프  📄 `spec/PLANNING-LOOP.md`(R0~R7·필수 스킬·종료 조건) · `spec/UEFN-DESIGN-SPACE.md` · `spec/INTAKE.md` · `spec/GENRE-PACKS.md`
라운드제. 시간 상한 없음, 종료는 조건으로만(종이 질문 0 · 전면공격 3회 연속 Blocker 0 · 미결 카드 0 · 페르소나 15판 · 사용자 확인). 라운드마다 필수 스킬을 선언하고 따른다(`grilling`·`domain-modeling`·`research`·`brainstorming`·`uefn-review`). 유일하게 사용자에게 묻는 구간이며 결정 카드로만 묻는다.
사람 → **형태 1개 + 비틀기 1개(DESIGN-SPACE 표 안에서)** → 컨셉 → 장르팩 → 코어루프 → 깊이 파기 → 팩 질문 → **맵 인테이크(`MAP-INTAKE.md`) → 플로우 검증(`loop/verify/flow.md`, fail 0)** → 기둥·MVP·티켓 해상도 → 네이티브 지수.
- 코어 형태는 DESIGN-SPACE §2 표에서만 고른다. 표 밖(2D·턴제·RTS·클릭커)은 연출 요소로만 허용하고 흉내 비용을 말한다.
- 한 번에 하나씩 대화한다. 중층(판단)·심층(숙련)이 없으면 되묻는다.
- 산출: `FUN-DEPTH.md` D-NN → `FUN-HYPOTHESIS.md` H-NN(지표·판정식·반증조건) → `GDD`·`systems`·`assets` · `MAP.md`(구역표·동선·플로우 매트릭스).
- 맵은 규칙의 그릇이다. 규칙마다 발동하는 자리, 자리마다 쓰는 규칙이 있어야 하며 플로우 표로 대조한다(맵 → 게임 → 플레이어가 어떻게 노는가).

### ①.5 실현가능성  📄 `spec/UEFN-FEASIBILITY.md`
핵심 메카닉 3~5개를 🟢직행 / 🟡우회 / ⚫GUI수동 / 🔴불가로 판정한다.
- 🔴가 코어면 기획을 바꾼다(같은 재미, 다른 수단). 🟡은 대체 설계 확정 후 티켓화. ⚫은 deferred 티켓.
- 실측: @editable 배선(최초·변경) 🟢 `bind_editable`(UEFN 닫고, 퍼블리시 수용만 미검증) · 자작 Verse `@editable` 설정값 🟢 · 스톡 디바이스 설정 ⚫ · 새 슬롯 추가 🟡 `add_binding` · 조준점 색 🔴.
- ⚫/🔴 판정 전에 반드시 `capabilities`를 호출하고 HARNESS §1.5를 대조한다. 라이브 거부("not valid ScriptDevice")는 불가 근거가 아니라 오프라인 몫이라는 신호다. `engine_devices` 검색 없이 "없는 디바이스"라 단정하지 않는다.

### ② DOR 게이트  📄 `spec/DOR.md`
5영역 체크 + 적대적 전면공격 1회(B-0 판단가능성 우선). Blocker 0이어야 착수. 미통과면 ①로 복귀. **여기가 마지막 질문 지점이다.** 자산 경로(블렌더·Fab·AI 생성 사용 여부)도 여기서 묻고, 쓰기로 했으면 전제조건(블렌더 실행·MCP 연결·Sketchfab/Hyper3D 키)을 상태 도구로 실행 확인한다.

### ③ 분해  📄 `plan/DECOMPOSE.md`
Plan(가설 1개) → Task(레벨 4개: A대조·B구조·C규칙·D인원) → Ticket(레벨당 4종). 레벨마다 한 축만 변경. 각 티켓에 구조수용·행동수용 기입.

### ④ 레벨 빌드 ×4  📄 `loop/LOOP.md` · `loop/TIMEBOX.md`
레벨당 뼈대30 · **비주얼30** · 배선35 · 측정로그30 · 자동실행30 · 리뷰20 · 예비5 = 180분.
매 티켓: 구현 → 구조검증(uefn-inspector, 에디터 OFF) → 행동검증(BuildAll→PIE→로그) → 적대적 빠른공격 3문항 → `done`. 레벨 완료 시 전면공격.
- A레벨에서 자동 구동 모드(봇/시뮬)를 먼저 만든다(+1h). 없으면 무인 루프가 돌지 않는다.
- 측정(티켓 3·4)은 빼지 않는다. 시간 부족 시 공간 디테일부터 컷.

### ⑤ 판정  📄 `spec/FUN-HYPOTHESIS.md` · `experiments/EXP-NN-results.md`
4레벨 지표 비교(B-A/C-A/D-A) → 지지 / 기각 / 애매 / 무효.
| 판정 | 다음 |
|---|---|
| 지지 | spec에 확정 기록 → ① 다음 가설 |
| 기각 | ① 인테이크(대안 가설) |
| 애매 | ③ 분해(축 하나만 바꾼 레벨 추가) |
| 무효(리뷰 Blocker) | ② 지표 수정 → 해당 레벨 재실행 |
⑤ 보고에는 4레벨의 플로우 리포트(실제 플로우·만남·재미 설명·재미 공백)를 붙인다. 그 뒤에 deferred 목록과 질문을 낸다.

## 절대 규칙 (규칙 0 다음)
1. 판단 가능성이 최우선이다. 정의·관측·구별·반증 중 하나라도 거짓이면 만들기를 멈추고 판단 가능한 상태부터 만든다(사람 호출이 아니라 지표 수정).
2. 사람은 루프 안에 없다. 자동 실행 + 로그 지표 + 규칙 판정.
3. 한 레벨 = 한 축만 변경.
4. 장르는 답이 아니라 질문의 안내자다. 관습 수치를 값으로 가정하지 않는다.
5. 표층만이면 반려한다(4층 중 3층 이상).
6. 측정은 빼지 않는다.
7. 안 되는 것을 된다고 하지 않는다. 역량 판단의 근거는 `capabilities` 도구 출력이며, 문서와 충돌하면 도구가 맞다. 실패는 실패로 보고한다.
10. **끝나면 플로우와 재미를 설명한다.** 레벨마다 `flow-report.md`(`loop/verify/flow.md` §6): 자동 실행 로그로 실제 플로우, 만남(언제·어디·누구·종류), 줄마다 재미를 지표·로그 근거로 설명. 근거 없이 설명 못 하는 줄은 재미 공백 → 그 줄을 겨냥한 수정 티켓으로 같은 레벨 재작업, 2회째도 공백이면 레벨 무효. 멀티는 역할별 플로우를 시간축으로 겹친 다인 표(§2)로 만남·상호작용·양쪽 재미를 미리 본다(F11~F16).
9. **구조는 설명할 수 있어야 한다.** 모든 레벨은 `build.md` 구조 절(테마 1줄 · 구역표: 이름/용도/평면도 기호/자산 · 동선: 스폰→첫 결정→목표→출구 좌표 · 뷰포트 스크린샷 3장)을 갖는다. 평면도·구역표는 `level_map`으로, 설계 됐는지는 `design_lint`(fail 0)로 중간 점검한다. 설명서 없는 뼈대는 `done` 불가, 남이 읽고 재현 못 하면 Blocker.
8. **비주얼은 기존 자산으로 채운다.** 그레이박스(S_Cube·기본 머티리얼)는 뼈대 티켓까지만 허용하고 레벨 완료 시점에 남아 있으면 Blocker. 자산 우선순위: 프로젝트 Content의 머티리얼·프롭 → Fortnite 갤러리/Playgrounds 프롭(라이브 `find_assets(folder_path)`) → 엔진 머티리얼. 새 에셋 제작·외부 반입은 deferred. 에디터에 보이는 것과 세션 유효(Disallowed reference)는 다르므로 비주얼 티켓의 수용은 StartSession 통과다. 절차는 `loop/visual.md`(의도→자산 조사→세션 유효성 스파이크→드레싱→조명→검증), 검증은 `loop/verify/structural.md` 6)과 ADVERSARIAL B-7.

## 도구  📄 `KIT/HARNESS.md`
- 라이브(uefn MCP `execute_python`·`get_editor_log`, unreal-mcp BuildAll): 배치·트랜스폼·컴파일·PIE·로그.
- 오프라인(uefn-inspector MCP): `capabilities`·구조검증·Verse-VM 값·@editable 배선 읽기/쓰기(`bind_editable`).
- 라이브 실패 → `capabilities` → 오프라인 → 그래도 없을 때만 GUI(deferred).

## 흔한 함정
자동 구동 모드 부재 · 라이브 실패를 "GUI 전용"으로 오판 · 오프라인 쓰기를 UEFN 켠 채 시도(파일 잠금) · 굿하트 오염(지표 만족시키며 재미없게 놀기 → 지표 교체) · 루프 중 질문으로 멈춤(규칙 0 위반) · 그레이박스로 레벨 완료 선언(규칙 8 위반) · 맨 도형만 놓고 구조를 설명 못 함(규칙 9 위반, `level_map`부터) · 에디터 렌더 성공을 세션 유효로 오인(WF-25).
