# checks/ — 재사용 검증 레시피

자주 쓰는 구조·행동 검증을 스크립트/절차로 모아둠. LOOP 4·5단계에서 호출.
예:
- `all_editable_wired.md` — 모든 Verse 디바이스의 선언 @editable이 배선됐나 (HeartMid류 감지)
- `settings_match_spec.md` — 디바이스 설정값 == spec/assets.md 기대값
- `pie_log_contains.md` — PIE 실행 후 로그에 기대 문자열 있나
