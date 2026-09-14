---
name: uefn-intake
description: Run the UEFN game-loop intake interview — ask what game, where the fun comes from, which genre pack applies, how deep the fun goes (4 layers/tension/failure modes), and how detailed tickets should be. Use when starting a new UEFN game or fleshing out an existing concept into spec documents.
---

# UEFN Intake — 게임을 캐내기

> 🔗 **이건 단축키다.** 전체 루프는 **`/uefn-game-loop`** 이 돈다 (①인테이크→②DOR→③분해→④레벨×4→⑤판정).
> 이 스킬의 위치: **① 인테이크**. 기각되어 되돌아온 경우 포함. 끝나면 ②DOR 게이트로.

**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit`

시작 전에 **반드시 읽는다**: `KIT/spec/PLANNING-LOOP.md`(라운드·필수 스킬·종료 조건) · `KIT/spec/UEFN-DESIGN-SPACE.md` · `KIT/spec/INTAKE.md` · `KIT/spec/GENRE-PACKS.md` · `KIT/spec/PERSONAS.md`

## 실행 방식 — 라운드제, 필수 스킬
인테이크는 한 번 훑는 질문지가 아니라 `PLANNING-LOOP.md`의 R0~R7을 도는 루프다. 라운드에 들어가면 **"Using <스킬> to <목적>"** 을 선언하고 그 스킬을 그대로 따른다.
| R | 스킬 | AI의 일 |
|---|---|---|
| 0 | `mattpocock-skills:domain-modeling` · `mattpocock-skills:research` | 용어집 `CONTEXT.md` · 참조 섬 3~5개 조사 |
| 1 | `superpowers:brainstorming` → `mattpocock-skills:grilling` | 형태 1개·비틀기 1개·왜 UEFN인가 → GDD §0 |
| 2·3·4 | `mattpocock-skills:grilling`(+3은 `domain-modeling`) | 재미 깊이 / 규칙·수치(경계값·동시발생·이탈·근거) / 맵 |
| 5 | AI 단독 (`flow.md` · `PERSONAS.md`) | 플로우 표 F1~F16 · 페르소나 15판 |
| 6 | `uefn-review` | 전면공격 B-0~B-9, 3회 연속 Blocker 0 |
| 7 | AI 단독 | 불확실성 두 목록 · 한 페이지 요약 · 종료 조건 |
grilling 형식(프론티어 질문 전부 + 번호 + 추천 답)이 결정 카드다. 답은 `DECISIONS.md`에 ADR로 남긴다. 아래 Phase 순서는 R1~R4 안에서 묻는 내용이다.

## 실행 순서

1. **Phase 1 창작발견** — 게임 아닌 **사람**부터: 몰입했던 순간과 *무엇이* 그 감정을 만들었나 ·
   오래 한 게임 3개 · 원하는 경험/기간/개발수준
2. **Phase 2 형태 선택 → 컨셉** — `UEFN-DESIGN-SPACE.md` §2에서 **형태 1개**, §3에서 **비틀기 1개**를 먼저 고른다(코어는 표 안에서만). 그 뒤 한 줄 피치 · **Core Verb** · Core Fantasy · Hook(=비틀기) · 최대 리스크 · 왜 UEFN인가
2.2. **표 밖 형태가 나왔을 때만** — `UEFN-FEASIBILITY.md` 0단계로 흉내 비용을 말한다. 🟡·🔴은 코어가 아니라 연출 요소로만. 2D·턴제·RTS·클릭커를 코어로 받지 않는다.
3. **Phase 2.5 장르 팩 선택** ⭐ — `GENRE-PACKS.md`에서 팩 1~2개(주/부) + 공통질문(승패·세션·**인원구조**·정보구조)
4. **Phase 3 코어 루프** — 30초/5분/세션/진행 각각의 **재미 원천**
5. **Phase 3.5 깊이 파기** ⭐ — 4층(감각→**판단**→**숙련**→이야기) · 긴장 대립쌍 · 실패모드 ·
   가장 불확실한 층 · **팩 필수질문 4개**
5.5. **Phase 3.7 맵 인테이크** ⭐ — `KIT/spec/MAP-INTAKE.md`: 구역 5종·첫 결정 지점·긴장 최고점 자리·순환/수직·랜드마크·시야·스폰 기하·경계·구조 축 변수 + 팩별 질문 → `spec/MAP.md`. 답마다 "이 자리를 쓰는 규칙"을 붙인다.
5.7. **플로우 검증** ⭐ — `KIT/loop/verify/flow.md`: 맵 구역 × 규칙 × 플레이어 플로우 표(S0 스폰 → 첫 결정 → 긴장 최고점 → 목표 → 종료)를 채우고 F1~F10 대조. fail 0이어야 DOR.
6. **Phase 4~6** — 기둥/안티기둥 · 플레이어/MVP · **티켓 해상도**
7. **UEFN 실현가능성** ⭐ — `KIT/spec/UEFN-FEASIBILITY.md`로 핵심 메카닉 등급 판정.
   🔴가 코어면 **기획을 바꾼다**(같은 재미, 다른 수단). 🟡은 대체 설계 확정, ⚫은 deferred 티켓(`capabilities`로 확인한 뒤에만).
8. **마지막 질문 지점** — 여기와 ②DOR까지만 사람에게 묻는다. 착수 후 루프는 묻지 않고 끝까지 돈다(LOOP 규칙 0). 종료 보고에서 받고 싶은 정보를 지금 확인한다.

## 산출 (문서에 기록)
`spec/FUN-DEPTH.md`(D-NN) → `spec/FUN-HYPOTHESIS.md`(H-NN, 지표는 팩에서 선별) →
`spec/GDD.md`·`spec/systems/`·`spec/assets.md` · `spec/MAP.md`(플로우 매트릭스 포함) → 그다음 `plan/DECOMPOSE.md`로 배분

## 규율
- **한 번에 하나씩** 대화로. 체크리스트 낭독 금지.
- 답이 **설계를 바꾸는 질문만**. 뻔한 건 기본값으로 정하고 통보.
- **중층(판단)이 없으면** 그건 메카닉이 아니라 이펙트 → 되묻는다.
- **심층(숙련)이 없으면** 금방 질린다 → 되묻는다.
- 장르 관습을 **값으로 가정하지 않는다**(질문의 안내자일 뿐).
- **디테일은 형태 안에서 판다.** 형태와 비틀기가 정해진 뒤에야 팩 필수 질문·깊이 파기를 던진다. 형태 없이 "무슨 게임 만들래"로 시작하지 않는다.
- 끝에 **네이티브 지수**(DESIGN-SPACE §4: 스톡 디바이스 비율 ≥70%, 파이프라인 개조 0, 표 안 형태, 왜 UEFN인가)를 계산해 GDD §0에 적는다.
- 종료는 `PLANNING-LOOP.md` 종료 조건 5개가 전부 참일 때만. 그 뒤 `spec/DOR.md`.
- 시간 상한 없음. 라운드 수·시간은 `state/session-log.md`에 적는다. 종이로 답할 수 있는 것을 빌드로 미루지 않는다.
