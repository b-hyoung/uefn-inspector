# UEFN-DESIGN-SPACE — UEFN이 잘 만드는 게임의 공간 (인테이크는 이 안에서 시작한다)

원칙: UEFN은 범용 엔진이 아니라 포트나이트 플랫폼이다. 잘 만드는 게임은 포트나이트가 이미 주는 것(3인칭 캐릭터·이동·무기·건설·탈것·NPC·스톰·팀/클래스·아이템·HUD·시네마틱)을 디바이스와 Verse로 조합한 게임이다. 카메라·물리·렌더 파이프라인을 바꿔야 하는 게임은 흉내에 그친다. 그래서 인테이크는 "무슨 게임을 만들까"가 아니라 **"이 공간에서 어떤 형태를 고르고 무엇을 비틀까"**로 시작한다.
상태: ✅ 이 kit에서 실측 / 📄 Epic 문서 / ❓ 미검증. 디바이스 이름은 `engine_devices`·라이브 `ListDeviceAssets`로 확인한다.

## 1. 네이티브 시스템 (재료)
| 시스템 | 대표 디바이스·API | 상태 |
|---|---|---|
| 전투 | 무기(Item Granter `add_item`)·Class Designer/Selector·Damage Volume·Elimination Manager | ✅ WF-26·30 |
| NPC | Guard Spawner·AI Patrol Path·Creature Spawner·Wildlife Spawner·Persona(대화 NPC) | ✅ 가드(Shadow Bait·BLACKOUT) / 📄 나머지 |
| 이동 | 스프린트·점프·맨틀·Teleporter·Launch Pad·Zipline·Grind Rail·Vehicle Spawner | ✅ Verse 좌표 텔레포트 / 📄 탈것 |
| 공간 규칙 | Zone(Mutator/Barrier/Capture Area)·Storm Controller(다단계)·Trigger·Timer | 📄 |
| 경제·진행 | Item Granter/Remover·Score Manager·Tracker·Save Point·Round Settings·Tycoon류 조합 | 📄 |
| 팀·라운드 | Team Settings·Class·Player Spawner·Team Inventory·Round/Island Settings | ✅ 팀 배정으로 봇 교전 |
| 정보·연출 | HUD Message·Map Indicator·Cinematic Sequence·Audio Player·Radio·Lights·Post Process·Day Sequence | ✅ 오디오·조명·어둠(WF-27·28) |
| 환경 | 랜드스케이프·Prop Manipulator·Prop Mover·Destructible·Water | 📄 |
| Verse | 상태머신·타이머·`@editable` 배선·`TeleportTo`·`GetPlayspace`·UI 위젯 | ✅ 게임 규칙·허브·측정 로그 |

## 2. 네이티브 게임 형태 (여기서 하나 고른다)
| 형태 | 코어 시스템 | 장르 팩 | 상태 |
|---|---|---|---|
| 존워즈·박스파이트(소규모 BR 전투) | 무기·건설·스톰·팀 | A | 📄 대표 모드 |
| 건게임·프리포올 | 무기 교체 규칙·Elimination·Score | A·D | 📄 |
| 레드 vs 블루 팀 슈터 | 팀·클래스·Capture Area | A·D·E | 📄 |
| 스텔스 침투·추격 | 가드 감지·조명·오디오 미끼·텔레포트 허브 | B | ✅ Shadow Bait |
| 어둠 생존·호러 | 가드·손전등·포스트프로세스 암흑·아이템 | B | ✅ BLACKOUT |
| 데스런·파쿠르 | 이동 디바이스·Damage Volume·체크포인트 | F | 📄 대표 모드 |
| 레이싱 | Vehicle Spawner·Race Manager·체크포인트 | F·D | 📄 |
| 타워디펜스·웨이브 방어 | Creature Spawner·건설·Score | A·G | 📄 |
| 타이쿤·자원 성장 | Item Granter/Remover·Tracker·Save Point·Prop Manipulator | G | 📄 대표 모드 |
| 프롭헌트·비대칭 숨바꼭질 | Prop Manipulator·팀·정보 비대칭 | B·D | 📄 |
| 탈출방·환경 퍼즐 | Trigger·Conditional Button·Prop Mover·힌트 오디오 | C | 📄 |
| 협동 웨이브·레이드 | 가드/크리처·클래스 역할·Team Inventory | E·A | 📄 |
| 롤플레이·소셜 허브 | Persona NPC·구역·경제·시네마틱 | E·G | 📄 |

형태 밖(2D·턴제·카드·리듬·RTS·클릭커)은 `UEFN-FEASIBILITY.md` 0단계의 흉내 비용을 진다. **코어는 이 표에서만 고른다.** 흉내 형태는 코어가 아닌 연출 요소로만 허용한다.

## 3. 비틀기 (형태에 얹는 한 가지)
형태 하나에 비틀기 하나. 둘 이상은 첫 세트에서 금지(한 축 변주 원칙과 같다).
- 정보: 어둠·소음·미니맵 제거·비대칭 시야 (B·D)
- 규칙: TTK·재진입·자원 압박·라운드 구조 (A·G)
- 공간: 수직성·안전지대·동적 지형(Prop Mover·Destructible) (C·F)
- 역할: 클래스 비대칭·1 vs N (D·E)
- NPC: 가드 행동·패트롤·미끼 반응 (B)
비틀기는 반드시 §1의 시스템으로 구현 가능해야 한다. Verse만으로 처음부터 짜야 하면 비틀기가 아니라 형태 이탈이다.

## 4. 네이티브 지수 (DOR에서 측정)
| 항목 | 기준 |
|---|---|
| 코어 메카닉 중 스톡 디바이스(+Verse 배선)로 구현되는 비율 | ≥ 70% |
| 카메라·물리·렌더 파이프라인 개조 | 0 |
| 형태 | §2 표 안 |
| "왜 UEFN인가" 한 줄 | 포트나이트 플레이어·자산·NPC·세션 중 하나를 근거로 답할 수 있음 |
미달이면 형태나 비틀기를 바꾼다. 지수는 `spec/GDD.md §0`에 기록한다.

## 5. 인테이크에서의 사용 순서
1. Phase 1(사람) 뒤, 컨셉을 묻기 전에 §2 표를 제시하고 형태 1개를 고른다(사용자가 말한 아이디어가 있으면 가장 가까운 형태로 대응시킨다).
2. §3에서 비틀기 1개를 고른다. 그 비틀기가 §1 어느 시스템으로 구현되는지 적는다.
3. 그 형태의 장르 팩 필수 질문 4개(`GENRE-PACKS.md`)와 깊이 파기(`INTAKE.md` Phase 3.5)를 **형태 안에서** 디테일하게 묻는다.
4. §4 지수를 계산해 DOR로 넘긴다.

## 근거
[Using Devices](https://dev.epicgames.com/documentation/fortnite/using-devices-in-fortnite) · [UEFN-Only Devices](https://dev.epicgames.com/documentation/fortnite/uefnonly-devices-in-fortnite) · [State of Unreal 2025 for Fortnite creators](https://www.fortnite.com/news/state-of-unreal-2025-highlights-for-fortnite-creators)(AI Patrol Path·Guard/Creature/Wildlife Spawner Verse API·Persona) · 대표 모드(존워즈·데스런·타이쿤·파쿠르·롤플레이): [Playhub 2026](https://playhub.com/blog/fortnite/best-creative-maps-152046) · 실측: `reports/2026-09-10-blackout.md`, `오류리스트/shadow-bait-이슈정리/`.
