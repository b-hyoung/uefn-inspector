# VISUAL — 비주얼 드레싱 루프 (레벨당 티켓 1.5, 30분)

목적: 그레이박스를 기존 자산으로 채워, 기능 요소가 한눈에 구별되고 세션에서 유효한 레벨을 만든다. 새 에셋 제작·외부 반입은 하지 않는다(deferred).
근거: Shadow Bait(프롭 갤러리 배치·컬러 조명), BLACKOUT 필드 리포트 WF-04·WF-25·WF-27·WF-28(`reports/2026-09-10-blackout.md`).

## 순서 (건너뛰지 않는다)
| # | 단계 | 시간 | 산출 |
|---|---|---|---|
| 1 | 의도 | 3분 | 시각 언어 1줄 + 기능 요소 매핑 |
| 2 | 자산 조사 | 5분 | 후보 메시·머티리얼 목록 |
| 3 | 세션 유효성 스파이크 | 5분 | 허용/거부 메시 목록 |
| 4 | 드레싱 | 10분 | 기능 요소 → 배경 순 배치 |
| 5 | 조명 | 3분 | 광원·노출 |
| 6 | 검증 | 4분 | census·스크린샷·StartSession·B-7 |

### 1. 의도
`levels/LEVEL-X/build.md` 비주얼 절에 적는다: 테마 1줄(예: 백스테이지·폐공장) + 기능 요소 매핑 표.
| 요소 | 무엇으로 보이게 | 후보 자산 |
|---|---|---|
| 목표 | 눈에 띄는 색·발광 | 예: 글로우스틱·컬러 라이트 |
| 위험(적·함정) | 붉은·어두운 | 예: 경고 프롭·붉은 라이트 |
| 경로 | 바닥·벽으로 방향 유도 | 예: 케이블·로드케이스 줄 |
| 안전지대 | 밝고 열린 | 예: 흰 라이트·비계 |
| 경계 | 통과 불가가 보이게 | 예: 벽 프롭·컨테이너 |
요소마다 다른 자산을 쓴다. 같은 자산을 두 요소에 쓰지 않는다(측정 오염).

### 2. 자산 조사 — 있는 것부터
1. 오프라인: 프로젝트 전체 인덱스로 이미 쓰인 머티리얼·메시를 센다(`structural.md` 6). 이전 레벨에서 세션 통과한 자산이 1순위.
2. `state/lessons.md` 비주얼 절의 허용/거부 목록을 읽는다.
3. 부족하면 라이브 `find_assets(folder_path=...)`로 폴더 단위 검색(전체 스캔은 플러그인 에러). 실측 폴더: `/Game/Playgrounds/Items/Props`(127개, 콘서트·비계·로드케이스·스피커), `/Game/Creative/Devices/Destruction_Object/Meshes/S_Cube`(허용 확인).
4. 후보는 요소당 2~3개, 총 20개 이내로 자른다.

### 3. 세션 유효성 스파이크 — 전부 깔기 전에
에디터에 보이는 것과 세션 유효는 다르다(WF-25: 환경 메시 5종이 StartSession에서 Disallowed reference로 거부, 에디터엔 정상). 후보 메시 종류별 1개씩만 배치 → `save_actor` → StartSession → 거부 목록 확인 → 거부 자산 제거. 허용/거부 결과를 `state/lessons.md`에 누적한다. 이 단계를 건너뛰고 전부 깐 뒤 거부당하면 티켓 시간을 다 잃는다.

### 4. 드레싱
- 순서: 목표 → 위험 → 경로 → 안전지대 → 경계 → 배경. 시간이 모자라면 배경부터 뺀다.
- 배치는 라이브 `add_to_scene_from_asset`. 이름에 인덱스를 붙인다(`V2B_cover_0`…, 중복 이름은 조용히 실패). 소량씩 간격을 두고 부른다(연속 대량 호출은 에디터 프리즈). 반환 refPath는 즉시 JSON 원장에 기록한다. `find_actors`는 부르지 않는다(30분 프리즈).
- 배치 후 `save_actor`. 안 하면 오프라인 census에 안 잡힌다.
- 트랜스폼만 바꾼 액터는 `save_packages([actor.get_outermost()], only_dirty=False)`로 명시 저장(WF-24). `Rotator`는 키워드 인자(roll·pitch·yaw)로만 쓴다(WF-23).
- 머티리얼 교체(`set_material` 등)는 미검증. 쓰려면 `capabilities`·실제 호출로 확인하고 `lessons.md`에 결과를 적는다. 확인 전에는 프롭이 가진 머티리얼로만 채운다.

### 5. 조명
- 광원 1개 이상, 비기본값(색·강도·반경). 요소 색과 맞춘다(목표=밝은 색, 위험=붉은 색).
- 회전이 필요한 빔은 `customizable_light_device`가 아니라 스포트라이트 `creative_prop`(라이트 디바이스는 회전 무시).
- 어둠 컨셉: 조명만 지우면 자동노출이 되살린다(WF-04). `PostProcessVolume`(unbound) `color_gain` 0.10 전후 + 노출 Manual·bias −3~−4(WF-28). 밤 시간은 `DaySequenceModifier` `day_night_cycle_time` 값만(시퀀스 에셋 참조는 Disallowed, WF-27).

### 6. 검증
1. 오프라인 census(`structural.md` 6): S_Cube 비율 ≤20%, 고유 머티리얼 ≥6, 고유 메시 ≥8(기본값, GDD §0에서 확정).
2. 뷰포트 스크린샷 3장(고정 카메라: 스폰 시점·목표 시점·부감)을 `levels/LEVEL-X/visual/`에 저장. 게임 클라이언트 캡처는 불가하므로 에디터 뷰포트로 본다.
3. StartSession 통과(Disallowed 0). 결과를 build.md에 기록.
4. ADVERSARIAL B-7을 스크린샷 기준으로 돌린다. Blocker면 4단계로 돌아간다.

## 결과 기록
`build.md` 비주얼 절(갤러리·census 수치·요소 매핑·StartSession 결과) + `state/lessons.md` 허용/거부 자산 목록.
