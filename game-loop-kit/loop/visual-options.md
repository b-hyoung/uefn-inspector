# VISUAL-OPTIONS — 비주얼 자산 확보 경로 목록 (조사 2026-09-14)

`loop/visual.md` 2단계(자산 조사)에서 어느 경로를 쓸지 고르는 표. 아래로 갈수록 품질 자유도는 오르고 비용·검증 부담·세션 거부 위험이 커진다. 상태: ✅ 이 kit에서 실측 / 📄 공식 문서 근거 / ❓ 미검증(쓰기 전 `capabilities`·실제 호출).

## 공통 제약 (모든 경로)
- 세션 유효성: 에디터에 보여도 StartSession에서 `Disallowed reference`로 거부될 수 있다(✅ WF-25). 종류별 1개 배치 → 세션 스파이크가 선행.
- 메모리: 섬 어느 지점이든 100,000 메모리 단위 초과 시 퍼블리시 불가. 레벨이 참조하는 모든 자산(메시·텍스처·랜드스케이프·디바이스)이 합산된다. 확인은 Project → Launch Memory Calculation, Window → Message Log → Memory Test Results(상위 100개). 📄
- 텍스처: 2의 거듭제곱 크기 + 밉맵 생성 필수(없으면 퍼블리시 검증 실패). 📄
- 반입 형식: 메시 FBX·OBJ·glTF·GLB, 텍스처 PNG·JPG·TGA·PSD·EXR 등, 오디오 WAV·OGG·FLAC. 반입 시 머티리얼 자동 생성은 디퓨즈·노멀만 연결. 📄
- 라이선스: Fab는 CC·Standard(Personal/Professional). UEFN용은 Included formats에 UEFN 태그가 있는 자산만. 외부 CC0(PolyHaven)는 자유, Sketchfab는 모델별 라이선스 확인.

## 경로 목록
| T | 경로 | 도구(이 환경) | 시간 | 상태 | 비고 |
|---|---|---|---|---|---|
| 0 | 프로젝트 안에 이미 있는 메시·머티리얼 재사용 | `material_usage`·`mesh_usage`(오프라인) | 분 | ✅ | 이전 레벨에서 세션 통과한 것이 1순위 |
| 1 | Fortnite 갤러리·Playgrounds 프롭 | 라이브 `find_assets(folder_path)` → `add_to_scene_from_asset` | 분 | ✅ Shadow Bait(`/Game/Playgrounds/Items/Props` 127개) | 전체 스캔 금지(플러그인 에러). 환경 메시 5종 거부 사례 있음 |
| 1b | 기본 도형 + 머티리얼 라이브러리(`M_EpicBase_Parent` 인스턴스, 색·러프니스만) | 라이브 `execute_python` 머티리얼 교체 | 분~십분 | ❓ | 머티리얼 교체 API가 저장되는지 미검증(디바이스 설정처럼 안 남을 수 있음, WF-01 유형) |
| 1c | 조명·포스트프로세스로 분위기 | `PostProcessVolume`·라이트·`DaySequenceModifier` | 분 | ✅ WF-04·27·28 | 자산 추가 없이 가장 큰 인상 변화. 스포트 빔은 `creative_prop` |
| 2 | 랜드스케이프 페인트(`MI_Fortnite_Customizable_01` 레이어) | GUI Landscape Mode | 십분 | 📄 | 지형이 있는 레벨만. 프로그램 접근 ❓ |
| 2b | UEFN 모델링 모드(Extrude·Boolean·UV·LOD·베이크) | GUI | 십분~시간 | 📄 | 기둥·벽 등 단순 형태. 반입 없이 세션 유효(자체 자산) |
| 3 | Fab 반입(UEFN 태그 자산) | UEFN 내 Fab 창(GUI) | 십분 | 📄 | 라이선스·메모리 확인. 반입 자체가 GUI → 루프 중엔 deferred |
| 4 | 블렌더 경유 반입 | Blender MCP(ahujasid, :9876) → FBX/glTF → UEFN Import | 시간 | ❓ | 아래 "블렌더 파이프라인" |
| 4a | └ CC0 라이브러리 | `search_polyhaven_assets`·`download_polyhaven_asset` | 분 | ❓ | 텍스처·HDRI·모델. 라이선스 문제 없음 |
| 4b | └ Sketchfab | `search_sketchfab_models`·`download_sketchfab_model` | 분 | ❓ | 모델별 라이선스·폴리 수 확인 |
| 4c | └ AI 생성 메시 | `generate_hyper3d_model_via_text/images`·`generate_hunyuan3d_model` | 십분/개 | ❓ | 리토폴·UV·폴리 감축 필수. 스타일 통일 어려움 |
| 4d | └ AI 텍스처(PBR) | 외부 생성기(PLAYTEX 등) → PNG 반입 → 머티리얼 인스턴스 | 십분 | ❓ | 2의 거듭제곱·밉맵 |
| 5 | 포토그래메트리·스캔 | 외부 → 블렌더 정리 → 4 | 시간~일 | ❓ | 폴리·텍스처 예산 초과 위험 최대. Nanite 유무는 UEFN 문서에 명시 없음 |

## 어디에 넣는가 (루프 위치)
- 레벨 티켓 1.5(30분) 안에서는 T0·T1·1c만 쓴다. 30분에 끝나고 세션 유효성이 검증된 경로다.
- T1b·T2·2b는 A레벨 자동 구동 모드처럼 A레벨에서 한 번 만들어 B·C·D에 복제한다(A레벨 +30분).
- T3·T4·T5는 루프 밖 **자산 티켓**(`plan/`에 ASSET-NN)으로 뺀다. 루프 착수 전이나 실험 사이에 돌리고, 산출은 프로젝트 Content에 반입해 다음 세트부터 T0이 된다. 루프 도중 필요해지면 deferred.
- 어떤 경로든 산출 자산은 세션 스파이크(종류별 1개 → StartSession)와 메모리 계산을 통과해야 `state/lessons.md` 허용 목록에 오른다.

## 블렌더 파이프라인 (T4, 자산 티켓)
1. 소스 확보: PolyHaven(CC0) 또는 Sketchfab(라이선스 확인) 또는 Hyper3D/Hunyuan3D 생성. 스타일 기준(팔레트·시대·스케일)을 먼저 1줄로 적어 섞이지 않게 한다.
2. 블렌더 정리: 스케일 1 unit = 1 cm(UE), 원점 바닥 중앙, 리토폴·폴리 감축, UV 1채널 + 라이트맵 UV, 텍스처 2의 거듭제곱(1K 기본, 주역만 2K), 머티리얼 슬롯 최소화, 콜리전 단순 메시(UCX_ 접두).
3. 반출: FBX(메시+머티리얼+텍스처 임베드) 또는 glTF/GLB.
4. UEFN 반입: Content Browser Import(디퓨즈·노멀만 자동 연결, 나머지 머티리얼은 수동). 프로그램 반입(`AssetImportTask`) ❓.
5. 검증: 세션 스파이크 → 메모리 계산 → 뷰포트 스크린샷 → `lessons.md` 허용 목록 등록.
6. 배치부터는 T0 경로(오프라인 census·라이브 배치).

## 근거
- [UEFN 자산 반입](https://dev.epicgames.com/documentation/en-us/fortnite/importing-assets-in-unreal-editor-for-fortnite) · [FBX 반입 튜토리얼](https://dev.epicgames.com/community/learning/tutorials/k4b8/fortnite-uefn-importing-static-meshes-using-fbx)
- [Fab in UEFN](https://dev.epicgames.com/documentation/en-us/fortnite/import-from-fab-in-unreal-editor-for-fortnite) · [Fab 라이선스](https://dev.epicgames.com/documentation/fab/licenses-and-pricing-in-fab)
- [모델링 모드](https://dev.epicgames.com/documentation/fortnite/modeling-mode-in-unreal-editor-for-fortnite) · [모델링 팁](https://dev.epicgames.com/documentation/en-us/fortnite/modeling-tips-in-unreal-editor-for-fortnite)
- [메모리 관리](https://dev.epicgames.com/documentation/en-us/fortnite/memory-management-in-unreal-editor-for-fortnite) · [텍스처 모범 사례](https://dev.epicgames.com/documentation/fortnite/textures-best-practices-in-fortnite) · [Project Size Tool](https://dev.epicgames.com/documentation/en-us/fortnite/project-size-tool-in-unreal-editor-for-fortnite)
- [머티리얼 라이브러리](https://dev.epicgames.com/documentation/en-us/fortnite/material-library-in-unreal-editor-for-fortnite) · [랜드스케이프 머티리얼](https://dev.epicgames.com/documentation/en-us/fortnite/editing-landscape-material-in-unreal-editor-for-fortnite) · [커스텀 머티리얼](https://dev.epicgames.com/community/learning/tutorials/dXy5/fortnite-custom-materials-in-uefn)
- 실측: `reports/2026-09-10-blackout.md` WF-01·04·23·24·25·27·28, `오류리스트/shadow-bait-이슈정리/02-우회해서해결한것.md` 8·10.
