---
name: uefn-review
description: Adversarially review whether a UEFN game's fun can actually be judged — attacking the definition, observability, discriminability and falsifiability of its metrics, plus dominant strategies, spec holes, metric gaming and experiment validity. Use when reviewing a design doc, a finished ticket/level, or experiment results before trusting a conclusion.
---

# UEFN Adversarial Review — "재미를 판단할 수 있나"

> 🔗 **이건 단축키다.** 전체 루프는 **`/uefn-game-loop`** 이 돈다 (①인테이크→②DOR→③분해→④레벨×4→⑤판정).
> 이 스킬의 위치: **리뷰 (②게이트 / ④티켓·레벨 / ⑤결과 검증)**. 루프 안에서 자동으로도 돈다. 단독 호출은 특정 산출물만 공격할 때.

**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit`
읽는다: `KIT/loop/review/ADVERSARIAL.md` (전체 체크리스트·등급·되먹임)

## 단일 질문
> ### **"지금 이 상태로 이 게임의 재미를 판단할 수 있는가?"**
"잘 만들었나"가 아니다. **판단 가능성**을 공격한다. 판단 불가 상태의 결론은 지지든 기각이든 **무효**.

## 모드
| 대상 | 모드 | 예산 |
|---|---|---|
| 티켓 하나 완료 | **빠른 공격** 3문항 | 2~3분 |
| 기획서 승인 · 레벨(Task) 완료 · 실험 결과 | **전면 공격** | 15~20분 |

### 빠른 공격 (3문항)
1. **속임수** — 이 수용기준을 **재미없는 상태에서도** 통과시킬 수 있나?
2. **우회** — 플레이어가 이걸 무시·우회할 수 있나? (그럼 관측해도 무의미)
3. **도미노** — 다음 티켓/레벨의 **측정을 오염**시키나?

### 전면 공격 — B-0 먼저 (통과 못 하면 나머지 생략)
1. **정의** — "재미있다"를 관측 가능한 문장으로 다시 말해봐라
2. **관측** — 어느 로그/값에 드러나나? 지금 실제로 찍히나?
3. **구별** — 재미있는 플레이 vs 없는 플레이를 넣으면 **값이 다른가?**
4. **반증** — **어떤 결과가 나오면 가설을 버릴 건가?** (못 답하면 실험이 아님)
5. **대리 오염** — 지표를 최대화하면서 **재미없게 노는 법**이 있나? (굿하트)

이후 B-1 재미(지배전략·10회차·지루한 구간·실력 반영) · B-2 스펙(모호·없는 규칙·가짜 층) ·
B-3 측정 · B-4 실험(축 2개 변경·표본·인과) · B-5 스코프.

### B-6. 역량 주장 공격 ⭐
- "그건 된다/안 된다"의 **근거가 실행 결과인가**, 추측인가? (`HARNESS.md` §1.5에 있나)
- **"GUI로만 가능"이라 단정한 것** 중 오프라인으로 되는 건 없나? (배선·설정값은 오프라인 가능)
- 반대로 **된다고 가정하고 설계한 것**이 실제로 호출해 본 적 있나?
> 잘못된 역량 주장은 **🔴 Blocker** — 그 위에 세운 계획·결론이 전부 흔들린다.

## 등급 → 처리
- 🔴 **Blocker** — 결론이 틀린다 → 중단·수정 (측정 문제면 **실험 무효·재실행**)
- 🟡 **Concern** — 결론이 약해진다 → 티켓화 + 결과에 한계 명시
- ⚪ **Nit** — `state/lessons.md`

## 리뷰어 규율
- **통과가 목적이 아니다.** "문제 없음"은 세 번 공격해도 안 뚫렸을 때만.
- 모든 지적은 **구체적 실패 시나리오**로 ("밸런스 이상" ❌ / "A만 쓰면 B가 무의미" ⭕).
- 근거 없는 수치·관습 금지. 모르면 **"측정 필요"**.
- **고치지 않는다** — 발견·등급만. 수정은 루프의 일.
- 깊은 심문이 필요하면 `mattpocock-skills:grilling`(design tree·frontier·라운드) 방식 사용.
