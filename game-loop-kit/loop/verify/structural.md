# 구조 검증 (uefn-inspector, 에디터 OFF)

"스펙대로 배치·배선·설정됐나"를 파일에서 확인. 에디터 없이·빠르게·비파괴.

## 도구
- MCP: `mcp__uefn-inspector__inspect_level`, `read_actor`, `editable_bindings`, `find`, `who_uses`, `audit`, `engine_devices`
- 라이브러리: `uefn_inspector.core.uasset` · `analysis.verse_source` · `analysis.verse`

## 레시피
### 1) 디바이스 배치 확인
`inspect_level(<레벨 디렉터리>)` → devices에 기대 클래스·개수 있나.

### 2) @editable 배선 확인 (Verse-VM)
`editable_bindings(<versedevice.uasset>)` → 각 슬롯이 기대 액터에 배선됐나.
(라이브 리플렉션·MCP가 못 읽는 것 — 여기서만 검증됨.)

### 3) 선언 ↔ 배선 교차검증 (드리프트/미배선 자동 감지) ⭐
```python
from uefn_inspector.analysis.verse_source import parse_verse, cross_reference
from uefn_inspector.analysis.verse import verse_bindings
from uefn_inspector.core.uasset import read_package
info = parse_verse(open("verse/<file>.verse",encoding="utf-8").read())
xref = cross_reference(info, verse_bindings(read_package("<placed.uasset>")))
assert xref["unwired"] == []   # 선언됐는데 미배선인 슬롯 = 버그
```

### 4) 설정값 확인
`read_actor(<file>)` → 프로퍼티 값(트랜스폼·Bool·Enum·설정)이 스펙과 일치.

### 5) 참조/무결성
`who_uses(path, 에셋)` · `audit(레벨)` → 깨진 참조·중복·경고.

### 6) 비주얼 census (규칙 8) ⭐
```python
from uefn_inspector.model.index import build_index
from uefn_inspector.analysis.analyze import material_usage, mesh_usage
idx = build_index("<레벨 디렉터리>")
mats, meshes = material_usage(idx), mesh_usage(idx)      # {에셋: [쓰는 액터...]}
default = [m for m in mats if m.endswith(("WorldGridMaterial", "M_Basic_Wall", "M_Basic_Floor"))]
cube = [m for m in meshes if m.endswith("/S_Cube")]
share = sum(len(meshes[m]) for m in cube) / max(1, sum(map(len, meshes.values())))
assert share <= 0.20 and len(mats) >= 6 and len(meshes) >= 8, (share, len(mats), len(meshes))
```
기본값(20%·6·8)은 예시이며 `spec/GDD.md §0`에서 게임별로 확정한다. 세션 유효성은 오프라인으로 못 잰다 → 라이브 StartSession 결과(Disallowed reference 0)를 `levels/LEVEL-X/build.md`에 기록.

### 7) 구조 설명서 (규칙 9) ⭐
`level_map(<레벨 디렉터리>, cell=500)` → 평면도(`map`·`legend`)·구역표(`zones`: 클래스별 개수·중심·범위)·`extent`·`unplaced`. 이 출력을 `levels/LEVEL-X/build.md` 구조 절에 붙이고 테마·구역 용도·동선(스폰→첫 결정→목표→출구 좌표)·스크린샷 3장 경로를 채운다. 이어서 `flow.md` ②: 플로우 표의 자리 열을 이 좌표로 바꾸고 `spec/MAP.md` 구역표와 대조(빠진 구역·좌표 없는 줄 = 미배치). `unplaced`가 있으면 위치 없는 액터이므로 배치 확인.

### 8) 디자인 린트 (중간 점검, 규칙 8·9) ⭐
`design_lint(<레벨 디렉터리>)` → 체크 11개(그레이박스 비율 · 고유 메시/머티리얼 · 불러다 쓴 출처 폴더 · 한 메시 점유 · 높이 층/z 범위 · 점유율 · 판 비율 · 축 이탈 회전 · 필수 기능 클래스 · 광원)를 ok/fail/unverified + 값 + 임계 + 근거로 반환. 뼈대 티켓 뒤와 비주얼 티켓 뒤에 돌리고, `fail`이 있으면 `done` 불가. 임계값은 `DEFAULT_PROFILE`이 기본이며 게임별 값은 GDD §0에서 확정해 `profile`로 넘긴다. `unverified`(스케일·회전 미직렬화)는 실패가 아니지만 스크린샷으로 대신 본다.

## 수용 판정
티켓의 **구조 수용** 항목을 위 레시피 결과와 대조 → 전부 일치해야 통과.
불일치 = 구현 수정 후 재검증(에디터 OFF 상태 유지).
