---
name: uefn-intake
description: Run the UEFN game-loop intake interview — ask what game, where the fun comes from, which genre pack applies, how deep the fun goes (4 layers/tension/failure modes), and how detailed tickets should be. Use when starting a new UEFN game or fleshing out an existing concept into spec documents.
---

# UEFN Intake — 게임을 캐내기

> 🔗 **이건 단축키다.** 전체 루프는 **`/uefn-game-loop`** 이 돈다 (①인테이크→②DOR→③분해→④레벨×4→⑤판정).
> 이 스킬의 위치: **① 인테이크**. 기각되어 되돌아온 경우 포함. 끝나면 ②DOR 게이트로.

**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit`

시작 전에 **반드시 읽는다**: `KIT/spec/INTAKE.md`(질문지) · `KIT/spec/GENRE-PACKS.md`(장르 분기)

## 실행 순서

1. **Phase 1 창작발견** — 게임 아닌 **사람**부터: 몰입했던 순간과 *무엇이* 그 감정을 만들었나 ·
   오래 한 게임 3개 · 원하는 경험/기간/개발수준
2. **Phase 2 컨셉** — 한 줄 피치 · **Core Verb**(가장 많이 하는 동작 1개) · Core Fantasy · Hook · 최대 리스크
2.2. **게임 형태 적합성** ⭐ — `UEFN-FEASIBILITY.md` 0단계. 2D·턴제·RTS·카드 등은 **형태 문제**.
   🟡=UEFN식 번역 확정 후 진행(예: 2D횡스크롤→고정 사이드카메라+축 제한) · 🔴=정직히 말하고 사용자 결정
3. **Phase 2.5 장르 팩 선택** ⭐ — `GENRE-PACKS.md`에서 팩 1~2개(주/부) + 공통질문(승패·세션·**인원구조**·정보구조)
4. **Phase 3 코어 루프** — 30초/5분/세션/진행 각각의 **재미 원천**
5. **Phase 3.5 깊이 파기** ⭐ — 4층(감각→**판단**→**숙련**→이야기) · 긴장 대립쌍 · 실패모드 ·
   가장 불확실한 층 · **팩 필수질문 4개**
6. **Phase 4~6** — 기둥/안티기둥 · 플레이어/MVP · **티켓 해상도**
7. **UEFN 실현가능성** ⭐ — `KIT/spec/UEFN-FEASIBILITY.md`로 핵심 메카닉 등급 판정.
   🔴가 코어면 **기획을 바꾼다**(같은 재미, 다른 수단). 🟡은 대체 설계 확정, ⚫은 GUI 티켓.

## 산출 (문서에 기록)
`spec/FUN-DEPTH.md`(D-NN) → `spec/FUN-HYPOTHESIS.md`(H-NN, 지표는 팩에서 선별) →
`spec/GDD.md`·`spec/systems/`·`spec/assets.md` → 그다음 `plan/DECOMPOSE.md`로 배분

## 규율
- **한 번에 하나씩** 대화로. 체크리스트 낭독 금지.
- 답이 **설계를 바꾸는 질문만**. 뻔한 건 기본값으로 정하고 통보.
- **중층(판단)이 없으면** 그건 메카닉이 아니라 이펙트 → 되묻는다.
- **심층(숙련)이 없으면** 금방 질린다 → 되묻는다.
- 장르 관습을 **값으로 가정하지 않는다**(질문의 안내자일 뿐).
- 끝나면 `spec/DOR.md`로 착수 가능 여부를 점검한다.
