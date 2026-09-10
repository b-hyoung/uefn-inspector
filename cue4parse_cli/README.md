# CUE4Parse CLI — 엔진 디바이스 카탈로그 직접 만들기

`engine_devices` 도구가 쓰는 `data/engine_device_catalog.json`을 **자기 Fortnite 설치본에서** 생성한다.

> ⚠️ **이 파일은 저장소에 포함되지 않는다.** Fortnite 콘텐츠 파생물이라 재배포하지 않는다.
> 각자 자기 머신에서 만들어 쓴다. **없어도 나머지 6개 MCP 도구는 전부 동작한다.**

## 필요한 것
| 항목 | 확인 |
|---|---|
| Fortnite 설치본 | `<FN>/FortniteGame/Content/Paks/*.utoc` |
| Oodle DLL | `<FN>/FortniteGame/Binaries/Win64/oo2core_*.dll` (게임에 동봉) |
| .NET SDK | `dotnet --version` (CUE4Parse 최신은 net10.0 필요) |
| AES 키 | 현재 빌드용 — 아래 참조 |

## 1) AES 키 받기
Fortnite paks는 암호화돼 있다. 현재 빌드의 메인 키를 공개 API에서 얻는다:
```bash
curl -s https://fortnite-api.com/v2/aes
```
→ `data.mainKey` 값을 쓴다. **패치마다 바뀌므로 그때그때 다시 받는다.**

## 2) CLI 프로젝트 만들기
```bash
mkdir uefn-inspector-cli && cd uefn-inspector-cli
dotnet new console -n EngineDump -o EngineDump
cd EngineDump && dotnet add package CUE4Parse
```

## 3) config.json (프로젝트 루트에)
```json
{
  "paksDir":  "D:/Fortnite/FortniteGame/Content/Paks",
  "oodleDll": "D:/Fortnite/FortniteGame/Binaries/Win64/oo2core_5_win64.dll",
  "aesMain":  "<위에서 받은 mainKey>",
  "version":  "GAME_UE5_6"
}
```
경로는 **포워드슬래시**로 쓴다(JSON 이스케이프 문제 회피).

## 4) Program.cs
```csharp
using System.Text.Json;
using CUE4Parse.Compression;
using CUE4Parse.Encryption.Aes;
using CUE4Parse.FileProvider;
using CUE4Parse.UE4.Objects.Core.Misc;
using CUE4Parse.UE4.Versions;

var cfg = JsonDocument.Parse(File.ReadAllText(args[0])).RootElement;
OodleHelper.Initialize(cfg.GetProperty("oodleDll").GetString()!);

var provider = new DefaultFileProvider(
    cfg.GetProperty("paksDir").GetString()!,
    SearchOption.TopDirectoryOnly,
    new VersionContainer(EGame.GAME_UE5_6));
provider.Initialize();
provider.SubmitKey(new FGuid(), new FAesKey(cfg.GetProperty("aesMain").GetString()!));
Console.WriteLine($"Mounted files: {provider.Files.Count}");

var devices = new SortedSet<string>();
foreach (var f in provider.Files.Keys)
{
    if (!f.EndsWith(".uasset")) continue;
    var name = f[(f.LastIndexOf('/') + 1)..^7];
    if (name.StartsWith("Device_") && !name.EndsWith(".o")) devices.Add(name);
}
File.WriteAllText(args[1], JsonSerializer.Serialize(new
{
    mountedFiles = provider.Files.Count,
    deviceCount = devices.Count,
    devices = devices.ToList(),
}, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine($"{devices.Count} devices -> {args[1]}");
```

## 5) 실행
```bash
dotnet run -c Release -- ../config.json <uefn-inspector>/data/engine_device_catalog.json
```
성공 예: `Mounted files: 2143959` · `1119 devices -> ...`

## 검증
```bash
python -c "from uefn_inspector.analysis.engine_catalog import search_engine_devices as s; print(s('AudioPlayer'))"
```

---

## 알려진 한계
- **usmap 없이는 카탈로그(이름 목록)까지만.** 엔진 에셋의 **프로퍼티 값·클래스 계층**을 읽으려면
  `.usmap` 매핑이 필요하다(cooked=unversioned). CUE4Parse가 usmap 없으면 로드를 거부한다.
- usmap은 커뮤니티 배포(FortniteCentral 등)에 의존하며, 시점에 따라 구할 수 없을 수 있다.
  구했다면 `provider.MappingsContainer = new FileUsmapTypeMappingsProvider(path);` 한 줄로 활성화된다.
- AES 키·포맷은 **패치마다 변한다.** 실패하면 키부터 다시 받는다.

## 법적 고지
생성된 카탈로그는 **Epic Games 콘텐츠 파생물**이다. 개인 사용에 한하고 **재배포하지 않는다.**
이 도구는 Epic Games와 무관하다. 자세한 내용은 저장소 `LICENSE`의 NOTICE 절 참조.
