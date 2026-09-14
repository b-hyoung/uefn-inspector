---
name: uefn-level
description: Build one UEFN variation level inside the 3-hour timebox — skeleton, mechanic wiring, measurement logging, unattended autoplay — verifying structure offline with uefn-inspector and behavior via PIE logs. Use when executing a level Task (LEVEL-A/B/C/D) from the game-loop-kit backlog.
---

# UEFN Level Build — 3시간 레벨 1개

> 🔗 **이건 단축키다.** 전체 루프는 **`/uefn-game-loop`** 이 돈다 (①인테이크→②DOR→③분해→④레벨×4→⑤판정).
> 이 스킬의 위치: **④ 레벨 빌드 (1개)**. 4레벨 중 하나. 끝나면 다음 레벨 or ⑤판정으로.

**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit`

읽는다: `KIT/loop/LOOP.md` · `KIT/loop/TIMEBOX.md` · `KIT/loop/visual.md` · `KIT/loop/visual-options.md` · `KIT/loop/verify/*.md`

## 착수 전
- **`spec/DOR.md` 통과 확인** (특히 **판단 가능성**: 지표가 재미있는/없는 플레이를 구별하나)
- 이 레벨이 바꾸는 **축 하나** 확인 (A대조/B구조/C규칙/D인원) → `levels/LEVEL-X/build.md`

## 티켓 4종 · 3시간 배분
| # | 티켓 | 예산 | 통과 기준 |
|---|---|---|---|
| 1 | 레벨 뼈대(공간·배치) | 30분 | `inspect_level`로 기대 디바이스·개수, 공간조건 |
| 1.5 | **비주얼 드레싱**(기존 머티리얼·프롭, 절차 `loop/visual.md`) | 30분 | `structural.md` 6): 기본 머티리얼 표면 ≤20% · 고유 머티리얼 ≥6 · 고유 메시 ≥8 · 기능 요소(목표·위험·경로·안전) 시각 구별 · StartSession 통과(Disallowed 0) |
| 2 | 메카닉 배선 | 35분 | `editable_bindings` **미배선 0** · 설정=변주조건 |
| 3 | 측정 로그 심기 | 30분 | PIE 로그에 지표별 `[M]` 라인 **전부** 출력 |
| 4 | 자동 실행·집계 | 30분 | N회 실행 → `metrics.md` 채워짐 |
| 5 | 적대적 빠른공격 ×4 + 전면 ×1 | 20분 | Blocker 0 |
| — | 예비 | 5분 | |

## 매 티켓
구현 → **구조검증**(uefn-inspector, 에디터 OFF) → **행동검증**(BuildAll→PIE→`get_editor_log`)
→ **빠른 공격 3문항**(`loop/review/ADVERSARIAL.md` A절) → 통과해야 `done`

## 절대 규칙
- **규칙 0 — 무정지.** 이 스킬은 DOR 통과 이후의 작업이므로 사람에게 묻지 않고 끝까지 간다. 막히면 `state/deferred.md`에 기록(무엇·왜·가정·영향)하고 보수적 가정으로 진행하거나 그 티켓만 `deferred`로 두고 다음 티켓으로. 파괴적 작업·새 의존성은 실행하지 않고 deferred. 질문은 레벨 보고 끝에 한 번에.
- **측정(티켓 3·4)은 못 뺀다.** 시간 부족하면 비주얼 밀도부터 줄이되 티켓 1.5의 최소 기준은 유지한다. 측정 없으면 이 레벨은 무효.
- **비주얼은 기존 자산으로**(규칙 8). 그레이박스 상태로 레벨 `done` 불가. 새 에셋 제작·외부 반입은 deferred. 세션 유효성(StartSession)이 수용 기준이다.
- 구간 3·4 초과가 예비까지 소진하면 → 레벨 `무효` 표시 후 다음 레벨(사람 호출 없음).
- **오프라인 쓰기는 UEFN 닫고**(파일 잠금). 표준 배치/값은 라이브 MCP로 열어둔 채.
- **@editable 배선은 오프라인으로 한다** — MCP `bind_editable(디바이스파일, 슬롯, 액터파일)`(UEFN 닫고).
  라이브 MCP가 거부("not valid ScriptDevice" 등)해도 **GUI 전용이라고 결론내리지 않는다** → `capabilities` 호출 → 오프라인 경로.
  퍼블리시 수용만 미검증이므로 사본·`.bak` 유지. `capabilities`에도 없을 때만 `deferred`(멈추지 않고 다음 티켓).
- **자동 구동 모드**(봇/시뮬)가 없으면 **A레벨에서 먼저 구축** — 없으면 무인 루프가 안 돈다.
- 한 레벨에서 **축 두 개 이상 바꾸지 않는다**.

## 도구
`mcp__uefn-inspector__*`(capabilities·inspect_level·editable_bindings·read_actor·audit·**bind_editable**) ·
`mcp__uefn__execute_python`/`get_editor_log` · unreal-mcp BuildAll
**순서:** 배치·트랜스폼·BuildAll·PIE = 라이브 / Verse-VM 값·@editable 배선 = uefn-inspector(오프라인).
라이브 실패 → `capabilities` → 오프라인 → 그래도 없을 때만 GUI.

## 끝나면
`levels/LEVEL-X/{build,autoplay,metrics}.md` 갱신 · `state/session-log.md`에 시간 기록 ·
Task 완료 시 **전면 공격**(B-0 판단가능성부터) → 4레벨 다 되면 `experiments/EXP-NN-results.md` 비교
