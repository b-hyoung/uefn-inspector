# 행동 검증 (라이브 PIE)

"실제로 스펙대로 작동하나"를 에디터 안 실행(PIE)으로 확인. 에디터 ON 필요.

## 도구
- MCP: `mcp__uefn__execute_python`, `mcp__uefn__get_editor_log`, `mcp__uefn__get_all_actors`
- 공식 `unreal-mcp` (Verse 컴파일)

## 전제 — 관측 가능하게 설계
Verse에 **디버그 로그**를 심어 관측 지점을 만든다(로그가 곧 행동검증 신호):
```verse
if (Debug?):
    Print("[TICKET-NN.MM.KK] <관측할 상태>: {값}")
```
가능하면 **SoloTest 스위치**로 혼자서도 조건을 재현(멀티 없이 검증).

## 레시피
### 1) Verse 컴파일
공식 MCP로 `ValkyrieToolset.VerseToolset.BuildAll` → 에러 0 확인.
(에러 있으면 → unreal-error-doctor류로 수정 후 재컴파일. 구현 단계로 복귀.)

### 2) PIE 실행 + 로그 관측
`execute_python`으로 PIE 시작 → 잠시 후 `get_editor_log` → 티켓의 **행동 수용** 문자열/상태가 로그에 나오나.
```
예) 로그에 "[TICKET-..] BPM 55->150" 이 거리 변화에 따라 출력 → 통과
```

### 3) 상태 스냅샷 (선택)
`get_all_actors`/`execute_python`으로 런타임 액터·컴포넌트 상태 조회(표준 프로퍼티 한정 — Verse-VM 런타임값은 리플렉션 한계).

## 수용 판정
티켓의 **행동 수용** = 로그/상태로 확인. 통과 못 하면:
- 3회까지 구현 수정 → 재검증. 그래도 실패 → **정지게이트**(원인 요약 보고).

## 주의
- PIE·덤프는 불안정할 수 있음 — 검증 끝나면 PIE 종료.
- Verse-VM 런타임 값은 리플렉션으로 못 봄 → **로그 관측**이 주 신호(그래서 Debug 로그 설계가 중요).
