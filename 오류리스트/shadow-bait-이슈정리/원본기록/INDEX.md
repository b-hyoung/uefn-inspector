# Shadow Bait — 문서 인덱스 (2026-09-10 기준)

> **여기부터 읽으세요.** 어떤 파일에 뭐가 있는지 지도.
> ⚠️ 표시는 **방향 전환(봇 자동측정 폐기 → 직접 플레이 테스트) 이전**에 쓰인 낡은 문서입니다.

---

## 🔵 1. 지금 봐야 할 것 (최신·유효)

| 파일 | 내용 |
|---|---|
| **`TODO.md`** | **남은 작업 전체** — 사용자가 할 것(GUI 배선 1회) / 배선 후 내가 할 것 / 실패 기록 / 지금 가능한 것 |
| **`PLAYTEST.md`** | **플레이 가이드** — 아레나 4개 좌표·테마, 조작법(빛끄기·미끼), 포털 이동법, 볼 것 5가지 |
| **`state/LESSONS-BLOCKERS.md`** | **막힌 점 총정리(가장 두꺼움)** — uefn-inspector/UEFN MCP/Verse/PowerShell 함정 전부. 원인·해결·미해결 분류 |

## 🟢 2. 기획 (유효 — 재미 정의의 원천)

| 파일 | 내용 |
|---|---|
| `spec/GDD.md` | 게임 정의 — 코어(유도하다), 디자인 기둥 4개, 확정 규칙, 미션·진행 규칙 |
| `spec/FUN-DEPTH.md` | 재미 4층 분해(표층/중층/심층/메타), 긴장쌍(영향력vs노출), 실패 모드 4개 |
| `spec/FUN-HYPOTHESIS.md` | 재미 가설 H-01, 지표 정의, 판정 규칙, 4레벨 변주 조건표 |
| `spec/UEFN-FEASIBILITY.md` | 🟢🟡🔴 실현가능성 판정 + **SPIKE 실측 결과**(무엇이 되고 안 되는지) |
| `spec/GENRE-PACKS.md`, `spec/INTAKE.md`, `spec/DOR.md` | 킷 원본 참고자료(질문지·게이트 기준) |

## 🟡 3. 현재 상태 기록

| 파일 | 내용 |
|---|---|
| `state/arenaV2_A~D.json` | **아레나 4개의 배치 액터 refPath 원장** — 삭제·수정 시 필수 |
| `state/game.json` | 게임 디바이스 + 목표 코인 12개 ref |
| `state/hub.json` | 텔레포트 허브 디바이스 + 포털 마커 ref |
| `state/SNAPSHOT.md` | ⚠️ v1 시절 상태(낡음) |
| `state/BLOCKERS.md` | ⚠️ 초기 블로커(EOS 인증 등). 최신은 LESSONS-BLOCKERS.md |
| `state/strays.json` | 중복 탐지 작업 산출물(임시) |

## 🔧 4. 도구 (재사용 가능)

| 파일 | 용도 |
|---|---|
| `tools/uecall.ps1` | **UEFN MCP를 raw HTTP로 호출** — 모든 자동화의 기반 |
| `tools/uewrite.ps1` | Verse 파일 쓰기 |
| `tools/build_arena_v2.ps1` | **아레나 빌더** — 지오+프롭+조명+디바이스+배선+저장 (A/B/C/D) |
| `tools/verify_arenas.py` | **오프라인 검증** — uefn-inspector로 배치가 스펙과 맞는지 (에디터 부하 0) |
| `tools/find_dupes.py` | 중복/잔여 액터 탐지 |
| `tools/build_arena_one.ps1` | ⚠️ v1 빌더(구버전) |
| `tools/build_arenas.ps1`, `cleanup_strays.ps1` | ⚠️ 실패한 초기 스크립트 |
| `tools/run_level.ps1` | ⚠️ 폐기된 봇 측정용 |

## 💻 5. Verse 코드

| 파일 | 상태 |
|---|---|
| **UEFN 안** `/TestProject/shadow_bait_game.verse` | ✅ **게임 규칙**(목표3·180초·승패) + @editable 슬롯 2개. 컴파일 clean |
| **UEFN 안** `/TestProject/shadow_bait_hub.verse` | ✅ **텔레포트 허브**(좌표 기반 포털). 컴파일 clean |
| `verse/shadow_bait.verse` | ⚠️ 첫 초안(미컴파일). 참고용 |
| `verse/shadow_bait_sim.verse` | ⚠️ 폐기된 봇 측정 시뮬 |

> ⚠️ 주의: 실제 동작하는 Verse는 **UEFN 프로젝트 안**(`Documents/Fortnite Projects/TestProject/Content/`)에 있습니다.
> `shadow-bait/verse/`의 것은 사본·초안입니다.

## ⚪ 6. 낡음 — 봇 측정 시절 (읽지 마세요)

- `experiments/EXP-01-results.md` — 측정 대기 상태로 멈춤(폐기)
- `levels/LEVEL-*/build.md`, `metrics.md`, `autoplay.md` — v1 좌표·봇 측정 전제
- `plan/PLAN-01/*`, `plan/PLANS.md` — 봇 측정 실험 계획
- `spec/USER-FLOWS.md` — v1 아레나 기준 유저플로우
- `loop/`, `HARNESS.md`, `README.md` — game-loop-kit 원본(방법론 참고서)

---

## 한 줄 요약

**최신 정보는 `TODO.md` + `PLAYTEST.md` + `state/LESSONS-BLOCKERS.md` 세 개**에 다 있습니다.
기획 의도는 `spec/GDD.md`·`FUN-DEPTH.md`, 실제 배치는 `state/arenaV2_*.json`.
나머지는 킷 원본이거나 폐기된 봇 측정 흔적입니다.
