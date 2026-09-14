# HARNESS — 이 kit이 쓰는 MCP·스킬 (실측 2026-09-14)

루프 각 단계에서 무엇을 호출하는지의 색인. 없는 것은 쓰지 않는다.

## 규율 — 안 되는 것을 된다고 하지 않는다
0. 이 문서보다 `capabilities` MCP 도구가 우선이다. 각 능력을 지금 실행해 ok/blocked/unavailable/unverified를 근거와 함께 돌려준다. 문서와 다르면 도구가 맞고, 문서를 고친다.
1. 표에 없으면 "된다"고 말하지 않는다. 모르면 "미검증"이라 말하고 확인한다.
2. 확인은 실행이다. MCP는 `claude mcp list` 후 실제 호출, 라이브러리는 실제 파일로 1회 실행, 설치물은 `node bin/cli.js doctor`.
3. "가능"과 "지금 이 환경에서 가능"은 다르다. 서버 꺼짐(unreal-mcp), 파일 없음(엔진 카탈로그), 에디터 열림(오프라인 쓰기)은 지금은 불가다.
4. 실패는 실패로 보고한다. 우회로를 찾되 됐다고 말하지 않는다.
5. 표가 틀리면 즉시 고치고 근거(실행 결과)와 날짜를 적는다.
6. "안 된다"고 말하기 전에도 같다. 라이브 호출 거부/실패("not valid ScriptDevice", 타입 거부, 설정 미저장) → 즉시 `capabilities` 호출 + §1.5 대조 → 있으면 오프라인으로 진행(쓰기는 UEFN 닫고) → 둘 다 없을 때만 "GUI 필요"이며 `capabilities` 결과를 근거로 첨부한다. 라이브 거부는 불가의 증거가 아니라 오프라인 몫이라는 신호다. ②를 건너뛴 GUI 판정은 리뷰 Blocker.

잘못된 가능성 주장은 실험 결과 무효이며 리뷰 Blocker 사유다.

## 1. MCP 서버
| 서버 | 종류 | 역할 |
|---|---|---|
| uefn-inspector | stdio(우리 도구) | 오프라인 전담(§1.5). `instructions`로 매 세션 시스템 프롬프트에 도구 분담이 주입된다 |
| uefn (KirChuvakov) | stdio → UEFN 리스너 :8765 | 라이브 조작 · `execute_python` · `get_editor_log`(행동검증) · 액터/에셋/뷰포트 |
| unreal-mcp (Epic) | http :8000 | Verse 컴파일(BuildAll) · 고정 툴셋. 에디터 ON 필요 |
| git | stdio | 티켓 단위 커밋 |
| blender-assets (ahujasid Blender MCP :9876) | stdio | 자산 티켓 전용(루프 밖): PolyHaven CC0·Sketchfab·Hyper3D/Hunyuan3D 생성 → FBX/glTF → UEFN 반입. 경로 표 `loop/visual-options.md` T4. 전제조건은 DOR에서 `get_scene_info`·`get_polyhaven_status`·`get_sketchfab_status`·`get_hyper3d_status`로 실행 확인 |

## 1.5 오프라인으로 되는 것 — uefn-inspector를 쓰는 이유
라이브 MCP·에디터 Python 리플렉션이 못 하는 것이다. 최종 판단은 `capabilities`.

| 하려는 것 | 도구 | 라이브 | 오프라인 |
|---|---|---|---|
| @editable 배선 읽기 | `editable_bindings` | ❌ | ✅ |
| @editable 슬롯 → 타 액터 배선(최초·변경) | MCP `bind_editable` · `edit.wire.bind_editable` | ❌ | ✅ 구조·리로드·런타임 검증 / ⚠️ 퍼블리시 수용 미검증(`reports/2026-09-10-blackout.md` WF-15). 사본 필수 |
| 기존 슬롯 재연결(동일 크기) | `edit.write.set_object_ref` | ❌ | ✅ UEFN 수용 확인 |
| 디바이스 설정값 읽기(Verse-VM) | `read_actor` | ❌ | ✅ |
| 설정값 변경(enum·스칼라) | `edit.write.set_enum` · `set_scalar` · `patch.patch_scalar_file` | 표준값만 | ✅ 에디터 닫고 |
| 새 @editable 슬롯 추가 | `edit.add_binding.add_binding` | ❌ | ⚠️ 크기변경, UEFN 수용 미검증 |
| 선언↔배선 교차검증 | `analysis.verse_source.cross_reference` | ❌ | ✅ |
| 인벤토리·검색·역참조·영향 | `inspect_level` · `find` · `who_uses` · `audit` | 크로스파일 ❌ | ✅ |
| 공간 분석 · **레벨 평면도·구역표**(구조 설명서) | `level_map` · `analysis.spatial.ascii_map` | ❌ | ✅ |
| **디자인 린트**(그레이박스·자산 다양성·출처·높이·점유·판·회전·광원) | `design_lint` · `analysis.design_lint` | ❌ | ✅ 중간 점검용 |
| 비주얼 census(머티리얼·메시 사용량, 그레이박스 비율) | `analysis.analyze.material_usage` · `mesh_usage` | ❌ | ✅ (세션 유효성은 라이브 StartSession만 판정) |
| 엔진 디바이스 카탈로그 | `engine_devices` | ❌ | ✅ 로컬 생성 시(`cue4parse_cli/README.md`) |

오프라인이 못 하는 것(라이브 몫): 게임 실행(PIE)·런타임 상태·로그 → `uefn`. Verse 컴파일 → `unreal-mcp` BuildAll. 액터·프롭 최초 배치 → 라이브 `PlaceDevice`·`add_to_scene_from_asset`. 프롭·머티리얼 탐색 → 라이브 `find_assets(folder_path=...)`(전체 스캔은 플러그인 에러). 세션 유효성 → StartSession(Disallowed reference).

운영 규칙
- 오프라인 쓰기는 UEFN을 닫고 한다(파일 잠금). 읽기는 켜져 있어도 된다.
- 표준 배치·트랜스폼은 라이브로. Verse-VM 값·배선은 닫은 김에 몰아서 오프라인으로.
- 분담 한 줄: 배치·트랜스폼·BuildAll·PIE·로그 = 라이브 / Verse-VM 값·@editable 배선 = 오프라인.
- 라이브 쪽 장애(로그아웃·런처·프리즈·도구 소실)는 `loop/recover.md`. 세션 전과 60분마다 `is_valkyrie_logged_in()` 확인.

## 2. 설계·프로세스 하네스
| 하네스 | 용도 | 쓰는 것 |
|---|---|---|
| `game-design-skill` v0.3.0 (Claude Code Game Studios, MIT) | INTAKE/GDD/시스템 문서의 근거 | `brainstorm` · `map-systems` · `design-system` · `design-review` · `balance-check` · `scope-check` · `playtest-report` · `propagate-design-change` · 템플릿 `game-concept`·`game-pillars`·`systems-index`·`game-design-document` |
| `ai-native-game-design` v0.2.0 | 런타임 AI 개입 메카닉 | `ai-native-game-design.md` · `ai-npc-design.md` |
| `narsha-adk` v0.9.12 | 개념 참고만(UE C++/라이브 전제) | `ue-audit` · `ue-impact` · `ue-diff` · `ue-validate` · `ue-plan-review` |
| `superpowers` v5.0.7 | 티켓 실행 규율 | `brainstorming` · `writing-plans` · `executing-plans` · `test-driven-development` · `systematic-debugging` · `verification-before-completion` |
| 기타 | — | `elements-of-style`(문서) · `impeccable`(UI) · `mattpocock-skills:grilling`(설계 심문) |

## 3. 루프 단계 ↔ 하네스
| 단계 | 쓰는 것 |
|---|---|
| 인테이크 | game-design `brainstorm` + `game-concept`/`pillars` 템플릿 → `spec/INTAKE.md` |
| 시스템 분해·규칙 | `map-systems` · `design-system` → `spec/systems/` |
| 티켓 배분 | `plan/DECOMPOSE.md` + superpowers `writing-plans` |
| 구현 | uefn MCP(라이브) · uefn-inspector(오프라인 쓰기) · superpowers TDD |
| 구조검증 | uefn-inspector(`loop/verify/structural.md`) |
| 행동검증 | uefn `get_editor_log` + PIE · unreal-mcp BuildAll(`loop/verify/behavioral.md`) |
| 밸런스·스코프 | `balance-check` · `scope-check` |
| 플레이테스트 반영·설계 변경 전파 | `playtest-report` → `state/lessons.md` · `propagate-design-change` |
