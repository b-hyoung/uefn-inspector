# BACKLOG — uefn-inspector

자율 루프용 티켓 보드. 각 티켓은 **수용 테스트(green이면 완료)** 로 완료를 정의한다.
사람은 매 스텝이 아니라 **티켓 정의 + 마일스톤 + 에스컬레이션**만 본다.

- py: `C:/Users/ACE/AppData/Local/Programs/Python/Python311/python.exe`
- 테스트: `<py> -m pytest -q`  (전부 green 유지가 불변식)
- 범위: **A(읽기 전용)**. 쓰기(B)는 사람 승인 게이트.

---

## 🔁 루프 실행 규약 (매 반복)

1. `BACKLOG.md`에서 **맨 위 `todo` 티켓** 하나 선택 → `doing`으로 표시.
2. **TDD**: 수용테스트를 RED로 작성 → 실패 확인 → 최소 구현 GREEN → REFACTOR.
3. `<py> -m pytest -q` **전체 green** 확인 (하나라도 깨지면 고치고 계속).
4. **커밋** (한 티켓 = 한 커밋, 메시지에 티켓 ID).
5. `capability-matrix.md`와 이 파일의 티켓 상태(`done`) 갱신.
6. 다음 티켓. **정지게이트**에 걸리면 멈추고 사람 호출.

## 🛑 정지게이트 (멈추고 사람 부르기)

- 설계가 모호하거나 스코프가 바뀔 때
- 매트릭스 **❌ 천장 항목**(Verse-VM 값·`@editable`) — 시도하지 말고 즉시 보고
- 수용테스트를 **3회** 시도해도 green 못 만들 때 (원인 요약해서 보고)
- **파괴적 작업**(원본 파일 덮어쓰기·삭제, 기본 자산 변경) — 사용자 전역 규칙
- 새 외부 의존성 추가가 필요할 때

---

## 티켓

상태: `todo` · `doing` · `done` · `blocked`

### T1 — 견고성: 손상/미지원 파일 graceful  · `todo` · P0
- **목표:** 잘린/비-uasset 바이트를 넣어도 예외 없이 `Package`(경고 포함) 반환.
- **수용테스트:** 랜덤 128바이트 임시파일 → `read_package` 예외 없음, `pkg.warnings` 비어있지 않음, `pkg.exports==[]`.

### T2 — 표준 태그드 프로퍼티 디코더  · `todo` · P1
- **목표:** export의 serial 영역에서 표준 프로퍼티(Bool/Int/Float/Name/Object/Enum)를 `{이름:값}`으로 디코드. 모르는 타입은 `unparsed`로 남기고 계속.
- **수용테스트:** `properties.decode(pkg, export)` → wall 또는 light 픽스처에서 최소 1개 표준 프로퍼티가 올바른 파이썬 값으로 나오고, `None` 안 터짐.
- **주의:** Verse-VM 프로퍼티(GUID 낀 것)는 대상 아님 → 정지게이트, `unparsed` 처리.

### T3 — 트랜스폼 읽기 (위치/회전/스케일)  · `todo` · P1  (T2 의존)
- **목표:** 배치 액터의 RootComponent 트랜스폼을 `PlacedActor.transform`에 채움.
- **수용테스트:** `inspect_actor(wall)` → `transform.location`이 유한한 float 3개, 전부 0은 아님(실제 배치 위치).

### T4 — CLI JSON 스키마 고정  · `todo` · P2
- **목표:** `--json` 출력 키/구조 계약을 테스트로 고정.
- **수용테스트:** `run(LEVEL_DIR)` 결과가 `level/actor_count/devices/asset_refs/warnings` 키를 갖고 JSON 직렬화 가능.

### T5 — 다른 레벨/파일 견고성  · `todo` · P2
- **목표:** MyProject의 두 번째 소스(예: `MyProject/Content/__ExternalActors__/MyProject`)도 크래시 없이 파싱.
- **수용테스트:** 해당 디렉터리 `inspect_level` → 예외 0, `warnings` 항목 각각이 심각한 실패가 아님(대부분 파싱 성공).

### T6 — 멀티코어 병렬 스캔  · `todo` · P3
- **목표:** `inspect_level(..., workers=N)`으로 대량 파일 병렬 파싱. 결과는 순차와 동일.
- **수용테스트:** 병렬 결과의 액터 집합 == 순차 결과 집합(순서 무관).

### T7 — [BLOCKED] B 쓰기 스파이크  · `blocked` · 사람 승인 필요
- **목표:** 표준 프로퍼티 1개를 오프라인으로 되써서 **UEFN이 받아주는지** 검증.
- **정지게이트:** 파괴적 → 반드시 사본에서, 사용자 승인 후에만. 루프는 이 티켓 건너뜀.

---

## 마일스톤
- **M1 (분석 견고화):** T1~T4 done → "믿을 수 있는 읽기 도구"
- **M2 (규모):** T5~T6 done → "대형 프로젝트 대응"
- **M3 (쓰기 탐색):** T7 (사람 주도)
