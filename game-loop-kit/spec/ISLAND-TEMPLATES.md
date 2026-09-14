# ISLAND-TEMPLATES — UEFN 섬 템플릿 목록과 수치화 (조사 2026-09-14, UEFN 6.0 / Fortnite 42.10)

용도: 기획 루프 R4(맵)에서 "어느 템플릿에서 시작할지"를 이름·썸네일 감이 아니라 수치로 정한다. 템플릿 파일은 디스크에 없고(`VKTemplates`는 가상 경로) 프로젝트 브라우저에서 생성해야만 나오므로, 수치는 **템플릿별로 프로젝트를 1회 생성해 uefn-inspector로 잰 값**만 적는다. 상태: ✅ 측정 / 📄 이름·썸네일 추정(측정 전).

## 측정 방법 (템플릿 하나 = 약 3분)
1. `loop/scripts/uefn_gui.ps1`로 프로젝트 브라우저를 열고 템플릿을 선택해 생성한다(`loop/recover.md` 절차 D). 이름은 `TPL_<템플릿>`.
2. 로드가 끝나면(에디터 켜진 채로 읽기 가능) `level_map`·`design_lint`·`inspect_level`을 `Content/__ExternalActors__`에 돌린다.
3. 배경 액터(`S_BackDrop`, `/Landscape/Background/`)를 뺀 **플레이 가능 액터**로 발자국·z 범위를 다시 잰다. 배경은 수백만 cm 밖에 있어 점유율을 0으로 만든다.
4. 아래 표에 한 행을 채우고, 프로젝트는 지운다(퍼블리시 안 함).

## 표 열 정의
| 열 | 뜻 |
|---|---|
| 액터 | 외부 액터 파일 수 / 배경 제외 수 |
| 발자국 | 배경 제외 x×y 범위(m) |
| z | 배경 제외 높이 범위(m) · 층 수(200cm 밴드) |
| 지형 | 랜드스케이프·수역·POI 유무(클래스 census) |
| 디바이스 | 배치된 디바이스 클래스(스폰·설정 등) |
| 린트 | `design_lint` fail 목록(그대로 쓰면 걸리는 것) |
| 맞는 형태 | `UEFN-DESIGN-SPACE.md` §2 형태 중 출발점으로 적합한 것 |

## 측정된 템플릿
| 템플릿 | 액터 | 발자국(m) | z(m)·층 | 지형 | 디바이스 | 린트 fail | 맞는 형태 |
|---|---|---|---|---|---|---|---|
| 심플 ✅ | 39 / 21 | 7.0 × 10.2 | −100 ~ +321 · 18 | 바닥 타일·오션 수역(WaterZone·VK_Waterbody_Ocean)·배경 15 | PlayerStart ×2 · ExperienceSettings · Decal · InspectorCamera | mesh_variety 6 · dominant_mesh 0.65(S_BackDrop) · lighting 0 | 형태 없음 — 빈 캔버스. 규칙 프로토타입(자작 Verse 디바이스 검증)용 |

## 미측정 템플릿 (프로젝트 브라우저 "섬 템플릿" 절, 2026-09-14 화면 기준, 스크롤 4장에서 확인된 24종 — 아래 더 있음)
| 템플릿 | 이름·썸네일로 본 성격 📄 | 우선 후보 형태 📄 |
|---|---|---|
| 기본 | 빈 바닥 | 규칙 프로토타입 |
| Grid Island · Large Grid Island · XL Grid Island | 평평한 격자 바닥, 크기 3단계 | 존워즈·박스파이트·건게임(아레나를 직접 짓는 형태) |
| Tilted Towers POI Island · Greasy Grove POI Island | BR의 실제 POI 하나가 놓인 섬 | 팀 슈터·소규모 BR·프롭헌트(기성 건물 활용) |
| Survival Island · Survival Island Empty · … with Caves · … with Caves Empty | 지형 섬, 동굴 유무, 프롭 유무(Empty) | 생존·추격·어둠 호러(동굴) · 협동 레이드 |
| Mountain Ridge Island · Mountain Ridge Island Empty | 능선 지형, 수직성 큼 | 데스런·파쿠르·스텔스(고저차 시야) |
| XL Archipelago Island · Archipelago Island · Horseshoe Island · Sandbar Island | 여러 섬·물 | 레이싱(탈것·보트)·이동 · 정보 비대칭(섬 간 거리) |
| Oasis Island · Meadow Island · Shoreline Island · Wasteland Island · Canyon Island | 테마 지형(사막·초원·해안·황무지·협곡) | 타이쿤·롤플레이 배경 · 협곡은 스텔스 동선 |
| Kevin Floating Island · Caldera Island | 특수 지형(부유 섬·화산) | 탈출방·환경 퍼즐 · 웨이브 방어(단일 진입로) |
| 브랜드 템플릿 · 기능 예시(Verse) | 브랜드 자산 / Verse 예제 프로젝트 | 기능 예시는 R0 참조 조사용, 시작 템플릿으로는 쓰지 않음 |

## 고르는 규칙
1. 형태(§2)가 정해진 뒤 위 표에서 후보 2~3개를 고른다. 후보는 반드시 측정해 첫 표로 올린 뒤 결정한다(📄 상태로 결정하지 않는다).
2. 직접 짓는 게임(아레나·박스파이트·탈출방)은 Grid 계열에서, 지형이 규칙인 게임(생존·추격·파쿠르·레이싱)은 지형 템플릿에서 시작한다.
3. 템플릿에 이미 있는 것(POI 건물·동굴·물)은 T0 자산이다. 비주얼 30분 티켓의 부담이 그만큼 줄어드므로, 같은 형태면 프롭이 많은 템플릿을 우선한다. 단 `Disallowed reference`는 템플릿 자산도 예외가 아니므로 세션 스파이크는 그대로 한다.
4. 결정과 근거(측정 행)는 `DECISIONS.md` 카드와 `MAP.md §크기`에 적는다.

## 알려진 함정
- `design_lint`의 점유율은 배경 액터 때문에 항상 0으로 나온다. 배경 제외 값을 별도로 재고, 린트 프로필에서 배경 클래스를 뺄 수 있게 하는 것은 다음 개선 항목이다.
- 템플릿 액터는 `_UAID_` 접미가 없다. uefn-inspector는 PersistentLevel 아래 export의 클래스로 판정한다(2026-09-14 수정).
- 새 프로젝트의 `.uefnproject`에는 `pythonExperimental`·`toolsets` 플래그가 없다. unreal-mcp(:8000)을 쓰려면 에디터를 닫고 플래그를 넣은 뒤 다시 열어야 한다(절차 D 후속).
