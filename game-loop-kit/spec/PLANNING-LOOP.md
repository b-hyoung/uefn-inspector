# PLANNING-LOOP — 기획 루프 (라운드제, 필수 스킬 지정)

목적: 기획을 한 번 훑는 질문지가 아니라 **라운드를 도는 루프**로 만든다. 종이로 답할 수 있는 것은 전부 여기서 답하고, 빌드가 필요한 것만 실험 가설로 남긴다. 기획 루프 안에서는 사용자에게 얼마든지 묻는다(규칙 0의 경계는 DOR 통과). 시간 상한은 없다. 종료는 시간이 아니라 아래 조건으로만 한다.
필수 스킬은 이 PC에 설치된 것만 쓴다(실측 2026-09-14: `mattpocock-skills` 1.2.3, `superpowers` 6.3.0, 이 kit의 `uefn-*`). 단계에 들어가면 **"Using <스킬> to <목적>"** 을 선언하고 그 스킬 절차를 그대로 따른다.

## 사전 점검 — 필수 스킬이 없을 때 (R0 첫 행동)
1. 세션의 스킬 목록에서 `mattpocock-skills:grilling`·`domain-modeling`·`research`·`superpowers:brainstorming`·`uefn-review`가 보이는지 확인한다. 문서가 아니라 목록이 근거다.
2. 하나라도 없으면 기획 단계이므로 사용자에게 **설치 카드 1장**을 낸다: 원인(플러그인 미설치 또는 비활성) · 명령 `node bin/cli.js plugins`(또는 `claude plugin install mattpocock-skills@claude-plugins-official`) · 설치 뒤 Claude Code 재시작 필요 · 추천 = 설치.
3. 사용자가 설치를 택하면 재시작 후 `/uefn-game-loop`으로 돌아온다(R0부터, 기록은 유지). 설치를 거절하면 **형식만 수동 적용**한다: 라운드·프론티어·번호 질문·추천 답을 이 문서의 규칙대로 직접 쓰고, `state/session-log.md`에 "grilling 미설치 — 형식 수동 적용"을 적는다. 이때 스킬 이름을 호출했다고 말하지 않는다.
4. `research`가 없으면 WebSearch로 직접 조사하고 같은 형식(`spec/research/`)으로 남긴다. `brainstorming`이 없으면 R1은 grilling만으로 진행한다. `uefn-review`가 없으면 kit 설치가 깨진 것이므로 `node bin/cli.js install`을 안내한다.
설치 여부는 `node bin/cli.js doctor`가 확인하고 `install`이 자동 설치한다(REQUIRED_PLUGINS).

## 라운드 표
| R | 단계 | 필수 스킬 | AI가 하는 일(정확히) | 산출 | 나가는 조건 |
|---|---|---|---|---|---|
| 0 | 준비 | `mattpocock-skills:domain-modeling` · `mattpocock-skills:research`(백그라운드) | 용어집 `spec/CONTEXT.md`를 열고 이후 모든 문서가 같은 말을 쓰게 한다. 같은 형태의 기존 포트나이트 섬 3~5개를 조사해 무엇이 재미고 무엇이 지루한지, 우리 비틀기가 다른지를 근거 링크와 함께 적는다(관습 수치는 값으로 쓰지 않는다) | `CONTEXT.md` · `spec/research/REF-ISLANDS.md` | 용어집 초안 + 참조 3개 이상 |
| 1 | 형태·비틀기 | `superpowers:brainstorming` → `mattpocock-skills:grilling` | 브레인스토밍으로 사용자의 아이디어를 `UEFN-DESIGN-SPACE.md` §2 형태에 대응시키고, grilling 라운드(프론티어 질문 전부 + 추천 답)로 형태 1개·비틀기 1개·"왜 UEFN인가"를 확정한다. 표 밖 형태는 흉내 비용을 말하고 코어로 받지 않는다 | `GDD.md §0`(형태·비틀기·네이티브 지수 초안) · `DECISIONS.md` 카드 | 프론티어 비어 있음 |
| 2 | 재미 깊이 | `mattpocock-skills:grilling` | `INTAKE.md` Phase 3·3.5와 장르 팩 필수 질문 4개를 grilling 형식으로 묻는다. 중층·심층이 비면 되묻는다. 답을 지표 후보·반증 조건으로 바꿔 적는다 | `FUN-DEPTH.md` D-NN · `FUN-HYPOTHESIS.md` H-NN 초안 | 4층 중 3층 · 긴장쌍 · 실패모드 3 · 지표마다 판정식 |
| 3 | 규칙·수치 | `mattpocock-skills:grilling` · `mattpocock-skills:domain-modeling` | 규칙마다 경계값·동시 발생·이탈·재접속·동점을 묻고, 수치는 초깃값·변주 범위·근거 3열 표로 받는다. 확정된 결정은 ADR로, 용어는 용어집으로 적는다 | `systems/*.md` · 수치 표 · `DECISIONS.md` · `CONTEXT.md` | "없는 규칙" 0 · 근거 없는 수치 0 |
| 4 | 맵·템플릿 | `mattpocock-skills:grilling` (+AI 단독 측정) | `MAP-INTAKE.md` A 11문 + 팩 B를 grilling 라운드로 묻는다. 답마다 "이 자리를 쓰는 규칙"을 붙인다. 시작 템플릿 후보 2~3개는 AI가 `ISLAND-TEMPLATES.md` 측정 방법대로 프로젝트를 만들어 재고(템플릿당 ~3분), 측정 행을 근거로 결정 카드 1장을 낸다 | `MAP.md` · `ISLAND-TEMPLATES.md` 측정 행 · 카드 | 구역 5종·동선·구조·시야·변주 채움 · 템플릿 확정 |
| 5 | 플로우·종이 플레이 | (AI 단독) `loop/verify/flow.md` · `PERSONAS.md` | 단일·다인 플로우 표를 채우고 F1~F16을 돈다. 페르소나 5종 × 역할별 3판 종이 플레이스루로 지배 전략·병목·재미 공백·규칙 구멍을 찾는다. 사용자 결정이 필요한 구멍만 다음 grilling 라운드로 넘긴다 | `MAP.md` 플로우 매트릭스 · `spec/playtests/PAPER-NN.md` | F1~F16 fail 0 · 15판 완료 · 구멍 전부 처리 또는 카드화 |
| 6 | 적대적 전면공격 | `uefn-review` | B-0 판단가능성 → B-8 네이티브성 → B-2 스펙·플로우 → B-1·B-3·B-4·B-5 → B-6 역량. 리뷰어는 고치지 않고 등급만 낸다 | 리뷰 기록(`state/reviews/R6-NN.md`) | Blocker 0 |
| 7 | 종료 판정 | (AI 단독) | 남은 불확실성을 두 목록으로 나눈다: **종이로 답 가능**(→ 해당 라운드로 복귀) / **빌드 필요**(→ 실험 가설로 `FUN-HYPOTHESIS`에 남김). 한 페이지 요약(피치·플로우·재미가 어디서·미해결)을 사용자에게 보인다 | `state/uncertainty.md` · 요약 | 아래 종료 조건 |

## 종료 조건 (전부 참일 때만 DOR로)
1. 종이로 답할 수 있는 불확실성이 0개다. 빌드 필요 목록은 비어 있지 않아야 한다(비면 실험할 것이 없다는 뜻이므로 가설을 다시 본다).
2. R6 전면공격이 **3회 연속** Blocker 0이다. 사이에 문서가 바뀌면 카운트를 다시 시작한다.
3. 결정 카드 중 미결이 0개다(`DECISIONS.md`).
4. 페르소나 플레이스루 15판이 끝났고 발견이 전부 처리 또는 카드화됐다.
5. 사용자가 한 페이지 요약을 보고 "이 게임 맞다"고 확인했다. 이것이 기획 루프의 마지막 질문이다.

## 사용자 시간 규칙
- 라운드마다 사용자에게 가는 것은 **결정 카드**만이다. 카드 = grilling의 한 질문(제목·선택지·추천 답·트레이드오프·바꾸는 문서). 뻔한 것은 기본값으로 정하고 통보한다. 사실 확인은 사용자에게 시키지 않는다(research·capabilities·engine_devices로 AI가 찾는다).
- 라운드 끝마다 한 페이지 요약을 갱신해 방향을 고칠 기회를 준다.
- **스킬 호출은 AI의 일이다.** 사용자는 `/uefn-game-loop` 한 번으로 시작하고 그 뒤 스킬 이름을 알 필요가 없다. AI 자동 호출 정책:
  · R1~R4에서는 `grilling`이 **기본값**이다. 질문이 하나라도 있으면 grilling 형식으로 낸다(일반 질문으로 묻지 않는다).
  · R0·R3의 용어·결정 기록은 `domain-modeling`, 외부 사실은 `research`, R1 발상은 `brainstorming`, R6은 `uefn-review`.
  · 기획 루프 밖(③ 분해·④ 빌드·⑤ 판정)에서 애매한 것이 나오면: DOR 통과 **전**이면 grilling으로 되돌아가 묻고, 통과 **후**면 규칙 0에 따라 묻지 않고 `state/deferred.md`에 적어 종료 보고에서 grilling 라운드로 한 번에 묻는다.
  · 사용자 전용 슬래시(`/grill-me` 등)는 있어도 되지만 절차의 일부가 아니다.

## 되돌아가기
R6 Blocker의 종류가 복귀 지점을 정한다. 판단가능성·측정 → R2, 네이티브성·형태 → R1, 스펙 구멍·수치 → R3, 맵·플로우 → R4·R5. 복귀 후에는 R5·R6을 다시 돈다.

## 기록
`DECISIONS.md`(카드·ADR) · `CONTEXT.md`(용어) · `state/uncertainty.md`(두 목록) · `state/reviews/`(R6 기록) · `spec/playtests/`(종이 플레이). 기획 루프에 쓴 라운드 수와 시간은 `state/session-log.md`에 적는다.
