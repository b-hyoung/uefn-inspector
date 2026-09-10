# Shadow Bait — 진행 중 막힌 점 총정리 (블로커 & 교훈)

> 2026-09-10 세션. uefn-inspector(오프라인 분석 MCP)와 unreal(UEFN 라이브 MCP)로 게임을 만들며
> 부딪힌 문제를 원인·해결·미해결로 분류. 다음 세션/사람이 같은 삽질 안 하도록.

---

## A. uefn-inspector (오프라인 분석 MCP) 관련

### A-1. `engine_devices` 카탈로그 없음 🟡 우회함
- **증상:** `engine_devices` 툴 호출 → "Engine device catalog not found at data/engine_device_catalog.json".
- **원인:** 카탈로그는 Fortnite 설치본 파생물이라 저장소에 없음(재배포 금지). 사용자가 직접 생성해야 함.
- **영향:** 디바이스 1119개 이름 검색 불가.
- **우회:** 라이브 MCP `DeviceToolset.ListDeviceAssets`(nameFilter)로 대체 — 실제 프로젝트에서 바로 검색됨.
  → **결론: engine_devices 없이도 디바이스 찾기 가능**(라이브 쪽으로).

### A-2. uefn-inspector는 "읽기 전용"이라 빌드엔 못 씀 (설계상)
- inspect_level / read_actor / editable_bindings = **구조 검증**엔 훌륭(에디터 꺼도 됨).
- 그러나 **맵을 짓는 것**(액터 배치·지오 생성)은 오프라인 파일 패치로 불가 = 새 파일 쓰기.
  → 빌드는 전부 라이브 MCP(unreal)로. uefn-inspector는 "다 짓고 나서 확인"용.
- **실측:** `inspect_level`로 배치된 VerseDevice_C·디바이스 수를 에디터 켜둔 채 정확히 읽음. ✅

### A-3. 테스트 픽스처 없음 (참고)
- 새 클론은 `tests/fixtures/*.uasset`가 없어 pytest 70개 중 66개 skip(정상, conftest 처리).
- 신규 테스트 2개(test_add_binding·test_rebuild_trailing)가 skip 목록 누락 → 로컬에서 conftest에 추가해 수정.

---

## B. UEFN 라이브 MCP (unreal / Valkyrie) 관련

### B-1. MCP 도구가 세션 레지스트리에서 사라짐 🟢 우회 해결
- **증상:** `mcp__unreal__*` 툴이 세션 시작 시 잠깐 끊긴 뒤 ToolSearch로 안 잡힘("no match").
  `claude mcp list`는 Connected로 표시. `unrealclaude` 브리지는 "editor not running" 오응답.
- **원인(추정):** 세션 중 서버 재연결이 harness 도구 인덱스에 자동 반영 안 됨.
- **해결:** **raw HTTP로 MCP 핸드셰이크 직접 수행**(`tools/uecall.ps1`). 포트 8000.
  initialize→Mcp-Session-Id→notifications/initialized→tools/call. `/mcp` 재연결 불필요.
  → 메타툴 3개(list_toolsets·describe_toolset·call_tool)로 전 툴셋 구동.

### B-2. 플레이 세션(PIE) 실행 실패 → 재로그인으로 해결 🟢
- **증상:** StartSession이 콘텐츠 업로드(CanStart)까지 가나 **플레이 클라이언트가 접속 못 하고** 서버 닫힘.
- **원인:** `ossv2_auth_token_refresh_failed: EOS_NotFound` + `FindSingleSession 404`. Epic 온라인 인증 실패.
- **해결:** **UEFN 재로그인** → EOS 토큰 갱신 → StartSession→CanStart→StartGame→**Running** 성공.
  플레이 클라이언트 정상 접속(client_proc 확인).
- **교훈:** 같은 계정으로 Fortnite를 따로 켜두면 EOS 토큰 충돌 가능 → **측정 중 Fortnite 별도 실행 금지**.

### B-3. 세션 상태 판단 기준 🟢 교훈
- StartSession 후 `SessionStatus=="Connected"`를 기다리면 **안 됨**(UpdatingContent에서 멈춤/Disconnected).
- **올바른 기준: `GameState`** — "CanStart"(게임 시작 가능) → StartGame → "Running".
- StartSession/StartGame은 오래 블록됨(~90s+) → 백그라운드 잡 + GameState 폴링 권장.

### B-4. 서버측 Print 로그 위치 🟢 교훈 (중요)
- **증상:** `SessionToolset.GetClientLogEntries(pattern)` → "No client log was found".
- **원인:** creative_device의 `Print`는 **서버측** 실행 → **에디터 로그**(`UnrealEditorFortnite.log`)에 남음.
  GetClientLogEntries는 **클라이언트** 로그를 읽음 → 서버 Print를 못 봄.
- **해결:** 측정 로그는 `%LOCALAPPDATA%\UnrealEditorFortnite\Saved\Logs\UnrealEditorFortnite.log`를
  `LogVerse: : [M] ...`로 grep. (run_level.ps1 이 방식으로 수정됨)

### B-5. 실행 중 verse 핫푸시 불가 🟡 교훈
- **증상:** 게임 Running 중 `PushChanges` → "The Refresh command is not currently available".
- **우회:** 새 Verse 반영하려면 **StopGame → StartGame**(재빌드된 코드 로드). 또는 StopSession→StartSession(전체 재업로드).
- ⚠️ 단, StopGame→StartGame이 **새 빌드를 항상 로드하는지 미확인**(측정에서 옛 코드 도는 정황 있었음 — 검증 필요).

### B-6. 이벤트 배선은 타깃 디바이스에 저장됨 🟢 교훈
- `AddEventBinding`은 `returnValue:null` 반환(성공/실패 구분 안 됨).
- `ListEventBindings`를 **소스** 디바이스로 조회하면 빈 배열 → **타깃** 디바이스로 조회해야 배선 보임.
- 조명엔 sourceEvents 없음(수신만). 스위치의 "On Turned On/Off"를 소스로, 조명 "Turn Off/On"을 타깃으로.

---

## C. Verse 컴파일 (BuildAll 진단으로 확인한 함정)
- `int / int` = **rational**(정수 아님). 정수는 제곱거리 비교로 우회하거나 Floor 필요.
- `if (c) then A else B` 표현식 — **then 키워드 필수**. 빠뜨리면 "Expected block".
- 순수함수를 `if` 조건에서 호출하려면 `<computes>`. 단 **클래스 생성(할당)** 함수는 `<computes>` 불가(default effect).
- 비교(`<=`,`>`,`and`)는 **loop 본문에 직접 못 씀**(실패 가능) → `if` 조건 안으로.
- 함수/변수명 `Err`는 Verse 내장과 **충돌**(ambiguous) → 다른 이름.
- 서버 device `OnBegin`은 플레이어 스폰 후 실행 → 클라 로딩 전엔 로그 안 나옴.

---

## D. 방향 전환 (사용자 지시)
- **봇 자동측정 시뮬레이션 폐기** — 사용자가 직접 플레이 테스트하기로. (2026-09-10)
- 이유: 봇 시뮬은 "재미 조건 형성"까지만 측정 → 진짜 재미는 사람이 플레이해야. 사용자가 직접 하는 게 빠름.
- 현재 작업: 실제 플레이 가능한 아레나 4개(A/B/C/D) 라이브 빌드로 전환.

---

## B-7. `find_actors`는 씬 전체 스캔 → **에디터 프리즈** 🔴 (중요)
- **증상:** `SceneTools.find_actors`(name 또는 actor_type) 호출 후 **에디터가 응답 정지**.
  MCP 전체 무응답(initialize조차 타임아웃), 에디터 로그가 12분+ 멈춤. 프로세스는 Responding=True(위장).
- **원인:** 레벨 오브젝트 50만 개(505,100) 규모를 스캔. `collision_channels` 필수 파라미터.
- **교훈:** **find_actors를 쓰지 말 것.** 대신:
  - 배치할 때 PlaceDevice/add_to_scene의 **반환 refPath를 즉시 JSON에 기록**(`state/arena_*.json` 방식) → 나중 삭제·배선에 사용.
  - 씬 전수 조사는 **uefn-inspector 오프라인**(inspect_level/build_index/inspect_actor)으로. 에디터 부하 0.
- **복구:** 에디터 재시작 필요(자동 복구 안 됨).

## B-8. 배치 액터는 저장해야 디스크에 보임 🟢 교훈
- OFPA(One File Per Actor)라 배치 직후엔 메모리에만 존재 → uefn-inspector가 못 봄.
- `SceneTools.save_actor`를 각 액터에 호출해야 `__ExternalActors__`에 기록되고 오프라인 분석 가능.
- 실측: 저장 전 23액터 → 저장 후 76액터.

## B-9. 빌트인 디바이스는 프로퍼티 조작 불가 🟡
- `DeviceToolset.ListDeviceProperties/SetDeviceProperty`는 **Verse ScriptDevice 전용**.
  빌트인(텔레포터·가드스포너 등)에 쓰면 "not valid ScriptDevice".
- 결과: **텔레포터 그룹 연결·가드 세부설정은 MCP로 불가 → GUI 필요.**
  이벤트 배선(AddEventBinding)은 빌트인끼리도 됨.

---

## C-2. PowerShell 함정 (자동화 스크립트에서 크게 헤맴)
- `switch`문 반환값은 **배열**. `$spec = switch(...)` 후 `$spec.half`가 단일요소 배열이 되어
  `$H*2`가 "op_Multiply 없음" 에러. **문자열 보간에선 정상처럼 보여** 디버깅이 매우 어려움.
  → `$H=[int](@($spec.half)[0])`로 강제 스칼라화.
- 함수가 `Write-Host` 아닌 **모든 미포획 출력을 반환값에 합침** → refPath 대신 배열 반환.
  → 반환은 `return $x` 명시 + 파싱은 정규식 헬퍼(`RefOf`)로 분리.
- Write 툴로 만든 .ps1의 **한글 주석이 CP949로 깨져 파서 에러**(BOM 없는 UTF-8).
  → 스크립트는 영문 주석 권장, 또는 인라인 실행.

---

## E. 미해결 / 진행 중
- **E-1. ~~스크립트 add_to_scene_from_class 실패~~ 🟢 해결** — 원인은 UEFN이 아니라 **PowerShell**
  (C-2의 switch 배열 + 함수 반환 오염). `build_arena_one.ps1`로 4개 아레나 전부 배치 성공.
- **E-2. 미끼→가드 유인 🔴 최우선 미검증** — 오디오 재생 배선은 확인. 그러나 **가드 AI가 소리를 듣고
  이동하는지 미확인**. 반응 안 하면 "유도" 메카닉 자체가 성립 불가 → Verse로 가드 목표 직접 조작 필요.
- **E-3. 상호 한 방 전투·승패 규칙 미구현** — 라운드 타이머·생존/처치 판정 없음. 현재 가드 기본 교전만.
- **E-4. ~~아레나 A 중복~~ 🟢 해결** — 대조군 A를 (-20000, 20000)에 새로 빌드해 해결.
  구 A자리(0,20000)엔 빈 껍데기(지오만) 잔존, 스폰패드 없어 무해.
- **E-5. ~~월드 원점 잔여 3개~~ 🟢 해결** — 지연 반영으로 결국 삭제됨.

## B-10. `remove_from_scene`의 `false`는 실패가 아닐 수 있음 🟡 (중요·헷갈림)
- 저장된 OFPA 액터 삭제 시 `returnValue:false`를 반환하지만 **실제로는 삭제되는 경우가 있음**
  (반대로 정말 안 되는 경우도 있음 — A2 삭제는 false 반환 후 실제로도 남음).
- 디스크 반영에 **수십 초 지연**이 있어 즉시 재검증하면 옛 상태가 보임.
- **교훈:** 반환값을 믿지 말고 **uefn-inspector 오프라인 재검증으로 확인**하되, 30~60초 뒤에 볼 것.
  이 지연 때문에 "A가 정리됐다 → 아니었다 → 됐다"로 판단이 두 번 뒤집혔음.

---

## G. v2 비주얼 빌드에서 배운 것 (2026-09-10 후반)
- **포트나이트 프롭 배치 가능** 🟢 — `SceneTools.add_to_scene_from_asset`에 BP 경로(`..._C`)를 주면 배치됨.
  쓸만한 폴더: `/Game/Playgrounds/Items/Props` (127개) — 콘서트 로드케이스·스피커·비계·무대·컬러 스포트라이트.
- **`find_assets`는 folder_path로 좁혀야 함** — 전체 스캔 시 엔진 플러그인 경로 에러(`AmbientAudio.uplugin`).
  `list_folders`는 파라미터명이 `root_path`(문서의 folder_path 아님).
- **액터 이름 중복 시 배치 실패** — `add_to_scene_from_asset`의 `name`이 같으면 조용히 실패.
  → 이름에 인덱스를 붙일 것(`V2B_cover_0`, `_1`...).
- **PowerShell: 배열 인덱싱 중간변수가 값을 잃음** 🔴 — `$a = @($P.x,$P.y)[$i % 4]` 후 함수에 넘기면
  빈 값이 전달됨(에러 없이). → 경로를 **직접 인자로** 넘기는 방식으로 회피.
  증상이 "Could not load asset at path: "(경로 공란)로 나타나 원인 추적이 어려움.
- **삭제 반영 지연 재확인** — remove_from_scene 후 오프라인에 반영되기까지 수십 초~수 분.
  206→143액터로 줄며 최종 정합. **성급히 재검증하면 오판**한다(B-10 참조).

## H. 설계 결함 (사용자 지적) + 세션 안정성 문제

### H-1. 🔴 "맵일 뿐 게임이 아니다" (사용자 지적, 타당)
- 아레나·조명·프롭·스위치만 있고 **규칙·승패·목표가 없었음**.
- 조치: `shadow_bait_game.verse` 작성(컴파일 clean) — 목표 3곳 터치=승리 / 가드에게 사망=패배 /
  180초 초과=패배 / 라운드 자동 반복. 목표 마커(코인 프롭) 12개 배치.
- 남은 결함: **무기 지급·상호 한 방 전투 없음**(아이템 설정이 GUI 전용), 미끼→가드 유인 미검증.

### H-2. 🔴 스폰 설계 결함 (사용자 지적, 타당)
- 스폰패드를 **4개 아레나에 각각** 배치 → 어디서 시작할지 불확실. 게다가 원 프로젝트의 기본
  `FortPlayerStartCreative` 2개가 월드 원점(허허벌판)에 잔존 → 아레나 밖에 떨어질 위험.
- 아레나 간 거리 300m라 걸어서 이동은 사실상 불가 → "레벨로 갈 수 없다".
- 조치(진행 중): **A 아레나 스폰만 남기고 B/C/D 스폰패드 삭제** → 항상 A 시작 → Verse 포털로 순환.
  포털은 `shadow_bait_hub.verse`(컴파일 clean, 좌표 기반 자동 감지, GUI 배선 불필요).
- 교훈: **이동 수단과 시작점을 먼저 설계**하고 콘텐츠를 배치해야 한다. 맵을 여러 개 만들 때
  "플레이어가 어떻게 그 맵에 도달하는가"가 맵 자체보다 선행 요건.

### H-3. EOS 인증이 1~2시간마다 만료됨 🟡 (반복)
- 재로그인으로 풀려도 **약 1시간 뒤 `ossv2_eos_login_recovery_query_token_failure`로 자동 로그아웃**.
  그 후 StartSession이 Unconnected에서 멈춤. 장시간 세션 작업 시 주기적 재로그인 필요.

### H-4. `remove_from_scene` 대량 호출도 에디터를 멈출 수 있음 🔴
- B/C/D 스폰패드 삭제 중 에디터 프리즈(로그 정지). find_actors(B-7)와 동일 증상.
- **교훈: 삭제/편집은 소량씩, 호출 사이 간격을 둘 것.** 대량 배치·삭제는 프리즈 위험.

## I. @editable 배선 자동화 — 최종 결론 🔴 (4경로 실패, 근거 확보)
> 사용자 지적("uefn-inspector 만들어뒀잖아")에 따라 전부 실측함. 결론: **최초 배선은 GUI 필수.**

**실측한 파일 구조 (게임 디바이스 uasset):**
- 슬롯 export/import는 Verse 선언+컴파일+save_actor만으로 **자동 생성됨**
  (`__verse_0x04365773_GuardSpawner`, import cls=`guard_spawner_device`)
- 그러나 그 export의 프로퍼티에 **`SavedActor`가 없음**(이벤트 서브객체 11개뿐).
  uefn-inspector의 `verse_bindings`는 이 SavedActor를 읽으므로 → `null` 반환.
- 게임 디바이스 import 60개에 **대상 액터 인스턴스 없음**.
- 가드 액터 파일(exports 50/imports 86)에도 **Verse 래퍼 객체 없음** → 에디터가 배선 시점에 생성.

**시도와 결과:**
| 경로 | 결과 |
|---|---|
| `SetDeviceProperty`(Verse ScriptDevice) | 프로퍼티 **노출은 됨**(`guardSpawner`,`decoyAudio`) 그러나 값 설정 시 "is not valid guard_spawner_device" — BP 액터를 Verse 클래스로 안 받음 |
| 서브오브젝트 경로 추측 3종 | 전부 실패(그런 export 자체가 없음) |
| `write.set_object_ref` | 불가 — SavedActor 신규 추가 + import 신규 추가 = **크기 변경**, `rebuild.py` fixup 엔진 미완 |
| `add_binding` | 용도 불일치 — 슬롯 export 복제용이지 배선 값 주입용이 아님 |

**교훈:** `SetDeviceProperty`는 **빌트인 디바이스엔 아예 불가**(not valid ScriptDevice), **Verse 디바이스엔 스칼라·enum만** 실용적. 오브젝트 참조(디바이스 간 배선)는 GUI 또는 fixup 엔진 완성이 필요.
**한 번 GUI로 배선하면** 그 뒤 다른 대상으로 *변경*은 `set_object_ref`로 오프라인 가능(동일 크기) — 이게 uefn-inspector의 검증된 강점.

## F. 최종 상태 (2026-09-10 세션 종료 시점)
- ✅ **v2 아레나 4개 완성** (백스테이지 테마·확대·프롭) — y=30000 선상
  A(-30000) 대조군 / B(0) 규칙축 / C(30000) 미로 / D(60000) 개방
- ✅ **4개 전부 스펙 정확히 일치** + 아레나 밖 잔여 0 (오프라인 검증, 총 143액터)
- ✅ v1 아레나 전부 삭제 정리 완료
- 크기: 52×52m (D는 84×84m), 벽 높이 7m · 아레나당 프롭 16~20개 + 컬러 스포트라이트
- ✅ 조명 스위치 배선·미끼 오디오 배선 완료(배선 저장 확인)
- ❌ 전투/라운드 규칙, 가드 소리반응 = 미구현/미검증
- 📄 플레이 가이드: `PLAYTEST.md`
