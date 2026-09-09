# ROADMAP — UEFN 오프라인 분석 키트

**목표(완성):** NarshaADK가 UE에 하는 분석의 폭만큼, UEFN `.uasset`/`.umap`을
**에디터 없이 오프라인으로** 분석하는 종합 키트. 인벤토리는 첫 조각일 뿐.

## 실측 근거 (MyProject, 우리 파서로 조사 2026-09-09)
- 파일: uasset 112 · umap 2 · verse 2 (Niagara/Sequencer/DataTable/Widget **없음**)
- 실재 자산: StaticMesh · **Material/MaterialInstance** · **CurveFloat** · SkeletalMesh · 크리에이티브 디바이스 · **_Verse(VerseDevice)**
- → 없는 시스템(니아가라 등) 분석은 **보류**(있는 프로젝트 발견 시 추가)

## 완성 구조 — 4계층
```
L0 파서 코어      uasset.py   충실한 모델(names/imports/exports/serial)     ✅
L1 프로젝트 인덱스 index.py    전 파일 파싱 → 패키지 + 참조 그래프(엣지)       🔜 최우선 신규
L2 분석 모듈      analyses/*  각 분석 = analyze(index)->Result, 독립 테스트   🔜
L3 출력          cli/report  분석 실행·JSON/사람용 리포트 (미래 MCP 래핑)     🔜(부분)
```
L1이 핵심 신규: 파일 하나가 아니라 **프로젝트 전체를 엮은 그래프**가 있어야
참조·의존·영향·검색 분석이 전부 그 위에 얹힌다.

## 분석 카탈로그 (feasibility)
✅ 오프라인 가능 · ⚠️ 부분(표준값 한정) · ❌ 천장 · ⏸ 보류(자산 부재)

| 그룹 | 분석 | 가능성 | NarshaADK 대응 |
|---|---|:--:|---|
| 기반 | 인벤토리(디바이스·에셋) | ✅완료 | 기본 |
| 기반 | **프로젝트 인덱스+참조 그래프** | ✅ | asset-discovery |
| 검색 | 에셋/디바이스 **검색**(이름·타입·클래스) | ✅ | ue_search_assets |
| 검색 | **where-used**(에셋이 어디서 쓰이나) | ✅ | ue-impact/xref |
| 검색 | **디바이스 설정 발견**(설정명·enum 나열) | ✅ | (지난번 못 찾던 것) |
| 의존 | 순환 의존 탐지 | ✅ | asset-discovery(circular) |
| 의존 | 영향 분석(X 지우면 깨지는 것) | ✅ | ue-impact |
| 의존 | 고아/미사용 에셋 | ✅ | asset-discovery |
| 검증 | 깨진 참조 탐지 | ✅ | ue-validate |
| 자산 | 메시 사용 분석 | ✅ | — |
| 자산 | 머티리얼/텍스처 사용 분석 | ✅ | ue-material |
| 자산 | 커브(CurveFloat) 분석 | ⚠️ | — |
| 프로퍼티 | 표준 태그드 값(Bool/Int/Float/Enum) | ⚠️ | — |
| 프로퍼티 | 트랜스폼/공간 배치 | ⚠️ | — |
| Verse | 배치 VerseDevice + @editable **슬롯명** | ⚠️ | blueprint-flow 유사 |
| 레벨 | audit/health(개수·중복·네이밍·경고) | ✅ | ue-audit |
| 레벨 | **diff**(버전 간 구조 차이) | ✅ | ue-diff |
| — | Verse-VM 설정**값**·@editable **값** | ❌천장 | (라이브 MCP) |
| — | 니아가라/시퀀서/DataTable | ⏸보류 | (자산 부재) |

## "완성" 정의
카탈로그의 ✅/⚠️ 티켓 전부 green + 실 MyProject로 검증. ❌는 명시 제외, ⏸는 자산 발견 시 개시.

## 마일스톤
- **M1 기반**: L1 인덱스 + 참조 그래프 + 검색/where-used
- **M2 의존·검증**: 순환/영향/고아/깨진참조
- **M3 자산·프로퍼티**: 메시/머티리얼/커브 + 표준값/트랜스폼
- **M4 레벨**: audit + diff
- **M5**: MCP 래핑 (분석들을 도구로 노출)
