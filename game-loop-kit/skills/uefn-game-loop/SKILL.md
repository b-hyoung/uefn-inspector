---
name: uefn-game-loop
description: Run the whole UEFN game loop end-to-end — intake (what game / where the fun is / genre pack / depth), readiness gate, decomposition into Plan→Task→Ticket, building 4 variation levels (structure/rules/player-count) inside a 3-hour timebox with offline structural verification and PIE behavioral verification, adversarial review at every ticket, and rule-based judgement of the fun hypothesis. Use for any UEFN game build/test/measure request; the other uefn-* skills are shortcuts into single stages of this loop.
---

# UEFN Game Loop — 루프 실행자

**이 스킬이 루프 전체를 돈다.** `/uefn-intake`·`/uefn-level`·`/uefn-review`는
**중간부터 들어오는 단축키**일 뿐, 기본 진입점은 여기다.

**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit`
규약 원본: `KIT/loop/LOOP.md` (이 스킬은 그 실행 절차서)

---

## THE LOOP

```
  ①인테이크 → ②DOR게이트 → ③분해 → ④레벨×4 → ⑤판정 ─┐
      ↑                                                  │
      └──────── 기각/애매/무효 → 해당 지점으로 복귀 ──────┘
```

### ① 인테이크 — 캐묻기  📄 `spec/INTAKE.md` + `spec/GENRE-PACKS.md`
사람→컨셉→**형태 적합성(0단계)**→**장르팩 선택**→코어루프→**깊이파기**→팩 질문→기둥·MVP·티켓해상도
- ⚠️ **형태 먼저:** "2D 게임"·"턴제"·"RTS" 같은 건 기능이 아니라 **형태 문제**.
  🟡(2D·턴제·카드·리듬)은 **UEFN식 번역 확정 후** 진행 · 🔴(RTS·클릭커·대규모)은 **정직히 말하고 사용자 결정**
- 한 번에 하나씩 대화로. **중층(판단)/심층(숙련) 없으면 되묻는다.**
- 산출: `FUN-DEPTH.md` D-NN → `FUN-HYPOTHESIS.md` H-NN(지표·판정식·반증조건) → `GDD/systems/assets`
- **일회성이 아니다** — ⑤에서 기각되면 여기로 돌아온다.

### ①.5 실현가능성 — "UEFN에서 되나?"  📄 `spec/UEFN-FEASIBILITY.md`
핵심 메카닉 3~5개를 🟢직행 / 🟡우회 / ⚫GUI수동 / 🔴불가 로 판정
- **🔴가 코어면 기획 변경** — 수단이 막히면 **같은 재미를 내는 다른 수단**으로 (재미는 목적, 수단은 교체 가능)
- 🟡은 대체 설계 **확정 후** 티켓화 · ⚫은 별도 티켓+정지게이트
- 실측 예: **@editable 기존배선 변경🟢**(uefn-inspector 오프라인, UEFN 닫고) · **디바이스 설정값🟢**(오프라인) ·
  새 @editable 슬롯 추가⚫(GUI) · 조명 벽통과🟡 · 조준점 색변경🔴(→오디오/포스트프로세스) · 외부통신🔴
- ⚠️ **라이브로 못 하는 것 ≠ 불가능** — 오프라인(uefn-inspector) 경로를 먼저 확인한다
- **단정 전에 `engine_devices` 검색** (디바이스 1119개)

### ② DOR 게이트 — 착수해도 되나  📄 `spec/DOR.md`
5영역 체크 + **적대적 전면공격 1회**(`loop/review/ADVERSARIAL.md` B-0 판단가능성 우선)
- **Blocker 0이어야 착수.** 가장 흔한 반려: 지표가 재미있는/없는 플레이를 **구별 못 함**.
- 미통과 → ①로 복귀.

### ③ 분해 — 티켓 만들기  📄 `plan/DECOMPOSE.md`
Plan(가설 1개) → Task(**레벨 4개**: A대조·B구조·C규칙·D인원) → Ticket(레벨당 4종)
- 레벨마다 **한 축만** 변경. 각 티켓에 **구조수용 + 행동수용** 기입.

### ④ 레벨 빌드 ×4 — 3시간씩  📄 `loop/LOOP.md` + `loop/TIMEBOX.md`
레벨당: 뼈대40 · 배선40 · 측정로그30 · 자동실행30 · 리뷰20 · 예비20 = **180분**
매 티켓: 구현 → **구조검증**(uefn-inspector, 에디터 OFF) → **행동검증**(BuildAll→PIE→로그)
→ **적대적 빠른공격 3문항** → 통과해야 `done`
레벨 완료 시 → **적대적 전면공격**
- A레벨에서 **자동 구동 모드**(봇/시뮬)를 먼저 만든다(+1h). 없으면 무인 루프가 안 돈다.
- **측정(티켓3·4)은 절대 못 뺀다.** 시간 부족하면 공간 디테일부터 컷.

### ⑤ 판정 — 기계가  📄 `spec/FUN-HYPOTHESIS.md` 판정식 + `experiments/EXP-NN-results.md`
4레벨 지표 비교(축별 효과 B-A/C-A/D-A) → **지지 / 기각 / 애매**
| 판정 | 다음 |
|---|---|
| 지지 | spec에 **확정** 기록 → **①** 다음 가설 |
| 기각 | **① 인테이크**(대안 가설 재발굴) |
| 애매 | **③ 분해**(축 하나만 바꾼 레벨 추가) |
| 무효(리뷰 Blocker) | **②** 지표 수정 → 해당 레벨 재실행 |

---

## 절대 규칙
1. **판단 가능성이 최우선** — "재미있나"보다 **"재미를 판단할 수 있나"**. 정의·관측·구별·반증 중 하나라도 거짓이면 만들기를 멈춘다.
2. **사람은 루프 안에 없다** — 자동 실행 + 로그 지표 + 규칙 판정. 사람은 **정지게이트에서만**.
3. **한 레벨 = 한 축만** 변경.
4. **장르는 답이 아니라 질문의 안내자** — 관습 수치를 값으로 가정 금지.
5. **표층만이면 반려** — 4층 중 3층 이상.
6. **측정은 못 뺀다.**
7. **안 되는 걸 된다고 하지 않는다** — 역량 판단은 **`capabilities` MCP 도구**가 근거다(문서 아님).
   그 도구는 각 능력을 **지금 실행해보고** ok/blocked/unavailable/unverified를 근거와 함께 반환한다.
   `HARNESS.md`는 참고일 뿐 — **충돌하면 도구가 이긴다.** 실패는 실패로 보고한다.
   ("가능"과 "지금 이 환경에서 가능"은 다르다: 서버 꺼짐·파일 없음·에디터 열림 → 지금은 불가)

## 정지게이트 (여기서만 사람 호출)
**새 @editable 슬롯 배선**(기존 배선 변경은 오프라인으로 가능) · 행동검증 3회 실패 · 스펙 모호/창작결정 · 파괴적 작업 · 새 외부 의존성

## 도구  📄 `KIT/HARNESS.md`
- **uefn-inspector** MCP — 구조검증·오프라인 읽기/쓰기·선언↔배선 교차검증
- **uefn** MCP — `execute_python`·`get_editor_log`(행동검증) · **unreal-mcp** — BuildAll
- 설계 렌즈: `game-design-skill` · 심문: `mattpocock-skills:grilling`

## 단축키 (중간부터 들어올 때만)
`/uefn-intake` = ① · `/uefn-level` = ④ 한 레벨 · `/uefn-review` = 리뷰 단독
> 전체를 돌 때는 이 스킬 하나로 충분하다.

## 흔한 함정
자동 구동 모드 부재(급소) · GUI 전용 배선(사람 대기) · 오프라인 쓰기는 **UEFN 닫고**(파일 잠금) ·
굿하트 오염(지표 만족시키며 재미없게 놀기) → 지표 교체
