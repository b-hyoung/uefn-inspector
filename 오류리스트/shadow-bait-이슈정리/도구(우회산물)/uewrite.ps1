# uewrite.ps1 — Verse 파일을 UEFN에 쓰기 (내용을 파일에서 읽어 JSON 이스케이프)
param(
  [Parameter(Mandatory=$true)][string]$VersePath,   # 예: /TestProject/shadow_bait.verse
  [Parameter(Mandatory=$true)][string]$ContentFile  # 로컬 파일에서 내용 읽음
)
$ErrorActionPreference = "Stop"
$s = Join-Path $PSScriptRoot "uecall.ps1"
$content = [IO.File]::ReadAllText($ContentFile)
$args = @{ path = $VersePath; content = $content; bCreateIfMissing = $true }
$inner = @{ name = "call_tool"; arguments = @{ toolset_name = "ValkyrieToolset.VerseToolset"; tool_name = "WriteFile"; arguments = $args } }
$pjson = $inner | ConvertTo-Json -Depth 20 -Compress
$out = & $s -Method "tools/call" -ParamsJson $pjson
($out | ConvertFrom-Json).result.content[0].text