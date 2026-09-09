# UEFN 오프라인 레벨 인스펙터 — 설계 (Spec)

- 날짜: 2026-09-09
- 상태: 승인됨 (brainstorming 완료)
- 범위: **A — 읽기 전용**. 쓰기·자동배선은 이 스펙 밖(별도 스파이크 B).

## 1. 목적

UEFN 에디터를 **켜지 않고**, 디스크의 `.umap` / `.uasset` 파일만으로 레벨에 배치된
디바이스와 그 설정을 읽어 구조화된 리포트로 뽑는다.

### 왜 필요한가 (근거)

세션 `06256ea8`에서 반복된 토일: 오디오 디바이스의 `Can Be Heard By`,
Verse의 `@editable` 바인딩 같은 설정이 **Verse VM 내부 데이터**라 런타임 리플렉션
(공식 MCP·에디터 Python 둘 다)으로 **못 읽혀서**, 매번 에디터 디테일 패널에서
손으로 확인해야 했다.

핵심 관찰: 런타임 리플렉션은 못 봤지만 **디스크 `.uasset`에는 태그드 프로퍼티로 저장돼 있다.**
실제 확인(`Content/__ExternalActors__/.../JK7E95WNLE67VPK9CQJKFO.uasset`):

```
Can Be Heard By
/Game/Creative/Devices/Common/Enums/ECreativeAudioPlayerTarget
/MyProject/Audio/Heartbeat_Near
Attenuation Falloff Distance / Attenuation Min Distance
/CRD_AudioPlayer/Device_CRD_AudioPlayer_C
```

따라서 이 도구는 "조사·검증" 절반의 토일을 오프라인 파일 읽기로 대체한다.

## 2. 전달 형태

순수 파이썬 **라이브러리 + CLI**. MCP 래핑은 후속(나중에 이 라이브러리를 감싼다).
외부 파싱 의존성 없음(파이썬 uasset 생태계 미성숙) — stdlib `struct`로 자체 파싱.

## 2.5 B-ready 구조 (지금은 A만 구현)

지금 구현은 A(읽기)뿐이지만, 미래 B(쓰기·되써넣기)가 재작업 없이 얹히도록 구조를 잡는다.

B는 "읽고 → 고치고 → 되쓰기"라, 리더가 이름 문자열만 대충 분류하면 B가 못 올라간다.
따라서 리더는 **바이트 주소를 아는 충실한(faithful) 모델**을 내놓는다.

**지금 확립할 불변식 (구조만, B 구현 아님):**

1. 이름 문자열이 아니라 **실제 객체 참조(imports/exports)** 로 모델링 — 분석 정밀도 ↑, 미래 수정도 참조 기반.
2. export는 **serial_offset / serial_size(바이트 영역)** 를 보유 — B가 프로퍼티 위치를 찾을 주소.
3. 리더는 **원본 바이트 유지** — 미래 라운드트립(읽은 걸 그대로 되쓰기)의 토대.

**B의 천장 (구조로 못 넘음):** `Can Be Heard By` 값·`@editable` 바인딩은 GUID 낀 비표준(Verse-VM)
직렬화라, 구조를 잘 잡아도 이 값들의 쓰기는 막힌다. B-ready가 여는 것은 주로 **표준 프로퍼티
편집 + 라운드트립**이며, Verse-VM 설정은 라이브 MCP 몫으로 남긴다.

## 3. 파싱 전략 — 점진적 하이브리드

1. **1단계 헤더 파싱**: `FPackageFileSummary → Name표 / Import표 / Export표`.
   비교적 안정적인 구조. 이것만으로 "배치 디바이스 클래스 + 참조 에셋 + 액터 이름"이 나온다.
2. **2단계 태그드 프로퍼티 값**: Bool / Int / Float / Name / Object참조 / Enum 부터.
   오디오 설정(`Can Be Heard By` enum 값, Attenuation 거리, 사운드 참조)을 우선 구현.

## 4. 아키텍처 — 유닛 (A 구현 4 + B 자리 1)

각 유닛은 하나의 목적, 명확한 인터페이스, 독립 테스트 가능.

| 유닛 | 입력 → 출력 | 의존 | 상태 |
|---|---|---|---|
| `uasset.py` 충실한 리더 | .uasset 바이트 → `Package{names[]+idx, imports[], exports[](serial_offset/size), raw}` | stdlib `struct` | A |
| `properties.py` 프로퍼티 디코더 | export 프로퍼티 영역 + name표 → `{설정명: 값}` (표준 타입, best-effort) | 리더 | A(부분) |
| `level.py` 레벨 모델/분석 | .umap + `__ExternalActors__/*.uasset`(OFPA) → `Level{PlacedActor[]}` | 리더+디코더 | A |
| `cli.py` 리포트/CLI | 프로젝트 경로 → JSON + 사람용 리포트 | 레벨 모델 | A |
| `writer.py` 라운드트립+표적수정 | `Package` + 수정 → 되쓰기 | 리더 모델 | **B·미래(자리만)** |

### 데이터 흐름

프로젝트 경로 → `.umap` + `__ExternalActors__` 수집 → 각 액터 파일: 리더로 파싱 →
import표에서 디바이스 클래스 해석 → 프로퍼티 디코드 → `PlacedActor` 조립 →
`Level` 집계 → JSON/리포트 출력.

### 데이터 모델

- `Package`: `{tag, file_version_ue, file_version_licensee, custom_versions[], names[], imports[], exports[]}`
- `PlacedActor`: `{name, uaid, device_class, transform?, settings{}, asset_refs[], unparsed[]}`
- `Level`: `{level_name, actors[PlacedActor], warnings[]}`

## 5. v1이 뽑는 것

- 배치 디바이스: 클래스(`Device_CRD_AudioPlayer`, `Device_ClassSelector_V2`, `Device_PointLight_V2`…), 인스턴스명/UAID, 트랜스폼(있으면)
- 참조 에셋: 사운드(`/MyProject/Audio/Heartbeat_Near`), 메시 등
- 디코드 설정: Bool(`bIsPlayerBuildable`, AutoPlay류), Enum(`Can Be Heard By` → `ECreativeAudioPlayerTarget` 값), Attenuation 거리(float)
- Verse 디바이스 + `@editable` 바인딩 참조: **best-effort**. 불확실하면 `unparsed`로 표시.

## 6. 에러 처리 (러스트 교훈 계승)

- 모르는 프로퍼티 타입 → 크래시 금지, `unparsed@offset`으로 기록하고 계속.
- 패키지 버전 불일치 → 경고 후 헤더는 계속 파싱.
- `__ExternalActors__` 없음 → 임베드 액터 파싱으로 폴백.
- 손상/예상 밖 바이트 → 해당 파일만 `warnings`에 남기고 나머지 진행.

## 7. 테스트 (TDD, 실제 파일 픽스처)

MyProject 실파일로 골든 테스트. 목킹 없음.

- 첫 픽스처: `.../__ExternalActors__/Level/PointLevel/6/3Q/JK7E95WNLE67VPK9CQJKFO.uasset` (AudioPlayer)
- 첫 테스트: "이 파일을 읽으면 device_class에 `Device_CRD_AudioPlayer`, asset_refs에 `Heartbeat_Near`가 있다"
- 이후: name표/import표 개수, `Can Be Heard By` enum 값, PointLevel 전체 디바이스 인벤토리

픽스처는 원본을 건드리지 않도록 `tests/fixtures/`로 **복사**해서 사용.

## 8. 비목표 (YAGNI)

- 쓰기·자동배선·자동토글 없음 (읽기 전용)
- Verse 의미 해석 없음 (참조만)
- 로컬 파일 전용, 원격/네트워크 없음
- 모든 UE struct 타입 디코딩 시도 안 함 — 필요한 것부터
- MCP 서버화는 후속

## 9. 안전 규칙 (사용자 전역 규칙 준수)

- 기본 자산·MyProject·나르샤 소스 **수정 금지**. 이 도구는 **읽기만** 한다.
- 픽스처는 복사본만 사용.
