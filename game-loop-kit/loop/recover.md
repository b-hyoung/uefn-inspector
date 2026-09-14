# RECOVER — 루프 중 환경 장애 복구 절차 (사람 호출 없이)

규칙 0에 따라 장애는 멈출 사유가 아니라 절차로 처리한다. 증상 → 원인 → 자동 조치 → 확인 → 기록 순서로 진행하고, 같은 절차가 2회 연속 실패하면 하드 실패로 종료 보고한다. 소요 시간은 `state/session-log.md` 초과 원인 열에 적는다.
근거: `reports/2026-09-10-blackout.md` WF-03·22·25, `오류리스트/…/02-우회해서해결한것.md` 1~5, 04-D. ❓는 이 저장소에서 아직 실행으로 확인하지 않은 항목.

## 증상표
| # | 증상 | 원인 | 조치 |
|---|---|---|---|
| R1 | `Play command is not currently available` · 전조 `ossv2_auth_token_refresh_failed EOS_NotFound` · `FindSingleSession 404` | Valkyrie 로그아웃. 토큰이 1~2시간마다 만료. 실패한 세션 쿠킹도 로그아웃을 유발 | **런처 URI 재기동**(아래 A) |
| R2 | A를 해도 로그인이 안 돌아옴 · 런처 창 무응답 · 새 exchange code 발급 안 됨 | 런처 프로세스 자체가 꼬임(사용자 실측 2026-09-14) | **런처 종료 후 재기동**(아래 B) |
| R3 | MCP 호출 전부 무응답, 에디터 CPU 점유 | 프리즈. `find_actors` 전체 스캔·대량 연속 호출 | 재시작하지 않고 에디터 로그 갱신을 감시(최대 30분, 두 번 다 자연 해소됨). 갱신이 끊기면 B |
| R4 | `mcp__unreal__*`·`mcp__uefn__*` 도구가 도구 목록에서 사라짐(`claude mcp list`는 Connected) | 세션 시작 시 서버가 잠깐 끊김 · 세션 중 등록한 서버는 재시작 전엔 안 잡힘 | **raw HTTP 직접 호출**(아래 C) |
| R5 | :8765 리스너 미응답 | `Content/Python/init_unreal.py`·`uefn_listener.py` 미복사 또는 UEFN 미기동 | 파일 존재 확인 → B |
| R6 | StartSession이 업로드 후 `Disallowed reference`로 중단 | 세션 금지 에셋 참조 | 해당 액터 제거·저장 → 오프라인 스캔으로 참조 0 확인 → 재시작. 이후 R1 여부 확인(쿠킹 실패가 로그아웃 유발) |
| R7 | `GetClientLogEntries`가 "No client log" | 서버측 `Print`는 에디터 로그에 남음 | `%LOCALAPPDATA%\UnrealEditorFortnite\Saved\Logs\UnrealEditorFortnite.log`를 `LogVerse: : [M]`로 grep |
| R8 | `remove_from_scene`이 false, `AddEventBinding`이 null | 반환값이 결과가 아님. 디스크 반영 지연 수십 초~수 분 | 30~60초 뒤 오프라인 재검증(`inspect_level`·`ListEventBindings(target)`) |
| R9 | 배치가 조용히 실패(20개 중 4개) | `add_to_scene_from_asset` 이름 중복 | 인덱스 이름(`V2B_cover_0`…)으로 재배치 |
| R10 | UEFN 프로젝트가 없음(첫 실행·새 게임) | 프로젝트 미생성 | **절차 D**로 생성. DOR 전제조건이므로 보통 기획 루프 끝에 처리 |

## A. 런처 URI 재기동 (R1)
1. `Start-Process "com.epicgames.launcher://apps/fn%3A1e8bda5cfbb641b9a9aea8bd62285f73%3AFortnite_Studio?action=launch&silent=true"` — 런처가 새 exchange code를 발급한다. UEFN exe 직접 실행은 1회용 코드라 불가.
2. UEFN 홈 화면에서 프로젝트 타일 **더블클릭**(단일 클릭은 선택만). 창 원점 기준 +640,+345, DPI-aware. 좌표는 머신별이므로 `state/env.md`에 기록해 둔다.
3. 리스너 응답까지 약 180초 대기 → `execute_python`으로 `is_valkyrie_logged_in()` 확인.
4. true면 원래 단계로 복귀. false면 B.

## B. 런처 종료 후 재기동 (R2·R3·R5)
1. 세션이 떠 있으면 `StopGame`. 저장 안 된 오프라인 변경이 있으면 `.bak`가 있는지 확인.
2. `Stop-Process -Name EpicGamesLauncher -Force`. UEFN(`UnrealEditorFortnite`)은 살아 있으면 두고, 로그가 30분 이상 멈췄거나 R5면 함께 종료.
3. A의 1~3을 다시 수행. UEFN을 종료했다면 타일 더블클릭 후 프로젝트 로드까지 추가 대기.
4. 로그인·리스너·:8000 셋 다 확인한 뒤 복귀. 실패하면 하드 실패로 종료 보고(질문이 아니라 보고).
5. ❓ 런처만 죽였을 때 UEFN 세션 인증이 이어지는지는 미확인. 첫 실측 결과를 이 문서에 적는다.

## D. 새 프로젝트 생성·준비 (✅ end-to-end 검증 2026-09-14, `loop/scripts/uefn_gui.ps1`)
프로젝트 생성은 GUI만 제공되지만 좌표 자동화로 끝까지 된다. `lore.exe repository create`는 버전관리 저장소 생성이라 해당 없고, 폴더 복제는 projectId가 Epic 서버 등록이라 불가하다. 아래는 실행해 확인한 순서와 소요다.

| # | 동작 | 함수 | 실측 |
|---|---|---|---|
| 1 | 런처 URI로 UEFN 기동 | `Uefn-Launch` | 프로세스 등장 ~5초 |
| 2 | 홈 화면 대기 → 스크린샷으로 좌표 확인 | `Uefn-Wait` · `Uefn-Shot` | 창 등장 60~300초(콜드 스타트는 300초 가까이) |
| 3 | "새 프로젝트" 클릭 → 프로젝트 브라우저(**별도 창**) | `Uefn-Click` | 즉시 |
| 4 | 템플릿 선택(결정 카드) · 스크롤 | `Uefn-Click` · `Uefn-Wheel` | 기본값은 "심플" |
| 5 | "생성" 클릭 → 폴더 생성 | `Uefn-Click` | 폴더 ~10초, 에디터 로드 ~40초 |
| 6 | 에디터 종료 | `Uefn-CloseEditor` | ~10초 |
| 7 | `.uefnproject`에 python·toolsets 플래그 | `Uefn-EnableProjectFlags` | `.bak` 남김, JSON 유효성 확인됨 |
| 8 | 재기동 → 홈에서 프로젝트 타일 **더블클릭** | `Uefn-Launch` · `Uefn-Click -Double` | 로드 ~300초 |
| 9 | unreal-mcp 확인 | `Uefn-PortOpen 8000` | ✅ 열림. MCP 핸드셰이크 성공, 도구 `list_toolsets`·`describe_toolset`·`call_tool` |

확인 신호: `<이름>.uefnproject`의 `projectId`가 새 GUID · 에디터 로그 `Selected Project (Direct)` · 창 제목에 프로젝트 이름 · 포트 8000 응답.

함정(전부 실측)
- **DPI 150% 모니터**: PowerShell은 DPI 비인식이라 창 좌표(논리)와 화면 캡처(물리)가 어긋난다. 스크립트가 `SetProcessDPIAware()`를 먼저 호출한다.
- **최소화된 창**: `GetWindowRect`가 (-32000,-32000)을 돌려줘 클릭이 화면 밖으로 나간다. `Uefn-Click`이 복원 후 rect를 다시 읽고, 그래도 음수면 예외를 던진다.
- **한글 IME**: `SendKeys`로 보낸 영문이 자모로 들어가 이름 검증에 걸린다. 이름은 클립보드(`^v`)로 넣되 브라우저 별창 포커스 문제로 아직 불안정(❓) — 실패하면 기본 이름 `MyProject`로 생성되므로 그대로 진행하고 deferred에 적는다.
- **좌표는 머신별**이다. 이 PC(창 2294×1626) 기준값은 스크립트 주석에 있고, 다른 PC에서는 `Uefn-Shot`으로 다시 잡아 `state/env.md`에 기록한다.
- 이 PC에는 uefn 리스너(:8765) 파일이 없어 `execute_python`·`get_editor_log` 경로는 미설치다. 행동검증이 필요하면 리스너 설치가 선행 조건이다.

## C. raw HTTP 직접 호출 (R4)
- unreal-mcp(:8000, MCP-over-HTTP): `initialize` → 응답 헤더 `Mcp-Session-Id` 보관 → `notifications/initialized` → `tools/call`. Shadow Bait `도구(우회산물)/uecall.ps1`이 이 절차를 구현했다.
- uefn 리스너(:8765): `POST {"command": ..., "params": ...}`(29 커맨드).
- 도구가 돌아올 때까지 이 경로로 계속 진행한다. 세션 재시작은 루프를 끊으므로 하지 않는다.

## 예방 (루프 스크립트에 내장)
- 세션 시작 전과 60분마다 `is_valkyrie_logged_in()` 확인, false면 A를 먼저 돈다.
- 비주얼 자산은 종류별 1개 세션 스파이크(`loop/visual.md` 3)로 R6를 사전에 막는다.
- `find_actors` 금지, 배치·삭제는 소량 + 간격 0.2~3초, refPath는 즉시 원장 기록.
- 세션 상태는 `SessionStatus`가 아니라 `GameState`(`CanStart`→`StartGame`→`Running`)로 판단한다. `StartSession`·`StartGame`은 90초 이상 블록하므로 백그라운드 + 폴링.

## 기록
- 발생 시각·증상 번호·조치·소요·결과를 `state/session-log.md`에 한 줄.
- 새 증상은 이 표에 행을 추가하고 `state/lessons.md`에 근거를 남긴다.
- 재기동 스크립트(로그인 체크+URI+타일 더블클릭)는 BLACKOUT 프로젝트에 있었고 이 저장소에는 없다. 이식은 자산 티켓으로 처리한다(deferred).
