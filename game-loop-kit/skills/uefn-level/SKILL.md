---
name: uefn-level
description: Build one UEFN variation level inside the 3-hour timebox — skeleton, mechanic wiring, measurement logging, unattended autoplay — verifying structure offline with uefn-inspector and behavior via PIE logs. Use when executing a level Task (LEVEL-A/B/C/D) from the game-loop-kit backlog.
---

# UEFN Level Build — 3시간 레벨 1개

> 🔗 **이건 단축키다.** 전체 루프는 **`/uefn-game-loop`** 이 돈다 (①인테이크→②DOR→③분해→④레벨×4→⑤판정).
> 이 스킬의 위치: **④ 레벨 빌드 (1개)**. 4레벨 중 하나. 끝나면 다음 레벨 or ⑤판정으로.

**KIT** = `C:\Users\ACE\Desktop\bobs_project\uefn-inspector\game-loop-kit`

읽는다: `KIT/loop/LOOP.md` · `KIT/loop/TIMEBOX.md` · `KIT/loop/verify/*.md`

## 착수 전
- **`spec/DOR.md` 통과 확인** (특히 **판단 가능성**: 지표가 재미있는/없는 플레이를 구별하나)
- 이 레벨이 바꾸는 **축 하나** 확인 (A대조/B구조/C규칙/D인원) → `levels/LEVEL-X/build.md`

## 티켓 4종 · 3시간 배분
| # | 티켓 | 예산 | 통과 기준 |
|---|---|---|---|
| 1 | 레벨 뼈대(공간·배치) | 40분 | `inspect_level`로 기대 디바이스·개수, 공간조건 |
| 2 | 메카닉 배선 | 40분 | `editable_bindings` **미배선 0** · 설정=변주조건 |
| 3 | 측정 로그 심기 | 30분 | PIE 로그에 지표별 `[M]` 라인 **전부** 출력 |
| 4 | 자동 실행·집계 | 30분 | N회 실행 → `metrics.md` 채워짐 |
| 5 | 적대적 빠른공격 ×4 + 전면 ×1 | 20분 | Blocker 0 |
| — | 예비 | 20분 | |

## 매 티켓
구현 → **구조검증**(uefn-inspector, 에디터 OFF) → **행동검증**(BuildAll→PIE→`get_editor_log`)
→ **빠른 공격 3문항**(`loop/review/ADVERSARIAL.md` A절) → 통과해야 `done`

## 절대 규칙
- **측정(티켓 3·4)은 못 뺀다.** 시간 부족하면 공간 디테일부터 컷. 측정 없으면 이 레벨은 무효.
- 구간 3·4 초과 → **즉시 정지게이트**.
- **오프라인 쓰기는 UEFN 닫고**(파일 잠금). 표준 배치/값은 라이브 MCP로 열어둔 채.
- **GUI 전용 @editable 배선** 만나면 → 별도 티켓 `blocked` + 정지게이트.
- **자동 구동 모드**(봇/시뮬)가 없으면 **A레벨에서 먼저 구축** — 없으면 무인 루프가 안 돈다.
- 한 레벨에서 **축 두 개 이상 바꾸지 않는다**.

## 도구
`mcp__uefn-inspector__*`(inspect_level·editable_bindings·read_actor·audit) ·
`mcp__uefn__execute_python`/`get_editor_log` · unreal-mcp BuildAll

## 끝나면
`levels/LEVEL-X/{build,autoplay,metrics}.md` 갱신 · `state/session-log.md`에 시간 기록 ·
Task 완료 시 **전면 공격**(B-0 판단가능성부터) → 4레벨 다 되면 `experiments/EXP-NN-results.md` 비교
