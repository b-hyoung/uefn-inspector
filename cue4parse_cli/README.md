# CUE4Parse CLI — 엔진 콘텐츠 추출기 (B 경로)

UEFN/Fortnite 엔진 cooked 콘텐츠(.pak/.utoc)를 마운트해 디바이스 카탈로그 등을
오프라인 추출한다. 프로젝트 파서(Python)와 별개인 C# 도구.

## 위치
`D:\uefn-inspector-cli\` (D드라이브 — C 공간 부족)
- `config.json` — paks 경로·Oodle dll·AES 키·버전
- `EngineDump/` — .NET 10 콘솔 (CUE4Parse 1.2.2)

## 검증된 상태 (2026-09-09, Fortnite 42.10)
- ✅ **마운트 2,143,959 파일** — AES 복호화 + Oodle + IoStore 작동
- ✅ **디바이스 카탈로그 1,119개** → `data/engine_device_catalog.json` (Python이 `engine_catalog.py`로 소비)
- AES 메인키: fortnite-api.com/v2/aes 에서 페치 (버전마다 갱신)
- Oodle: `oo2core_5_win64.dll` (게임 설치본)

## 실행
```
cd D:/uefn-inspector-cli/EngineDump
dotnet run -c Release -- ../config.json ../device_catalog.json
```

## ⏳ 남은 것 — usmap (프로퍼티 값·전체 클래스 계층)
엔진 cooked 에셋은 **unversioned** → 프로퍼티 **값**과 완전한 클래스 계층 디코드에
**.usmap 매핑**이 필요. 현재 상태:
- 자체 생성 = **EAC(안티치트)로 주입 차단** → 불가
- 커뮤니티 소스 = **FortniteCentral API가 현재 다운**("no available server")
- → 서비스 복구 시 또는 **FModel 설치**(usmap 자동 관리)로 해금. 그러면 CUE4Parse에
  `provider.MappingsContainer = new FileUsmapTypeMappingsProvider(usmapPath)` 로 값·계층까지.

카탈로그(뭐가 있나)는 usmap 없이 됨. 값/계층은 usmap 대기.
