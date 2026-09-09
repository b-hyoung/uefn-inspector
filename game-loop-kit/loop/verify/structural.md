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

## 수용 판정
티켓의 **구조 수용** 항목을 위 레시피 결과와 대조 → 전부 일치해야 통과.
불일치 = 구현 수정 후 재검증(에디터 OFF 상태 유지).
