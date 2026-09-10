# uecall.ps1 — UEFN MCP(HTTP) 직접 호출 헬퍼
# 사용: powershell -File uecall.ps1 -Method "tools/list"
#       powershell -File uecall.ps1 -Method "tools/call" -ParamsJson '{"name":"...","arguments":{...}}'
param(
  [Parameter(Mandatory=$true)][string]$Method,
  [string]$ParamsJson = "{}"
)
$ErrorActionPreference = "Stop"
$u = "http://127.0.0.1:8000/mcp"
$H = @{ "Accept"="application/json, text/event-stream"; "Content-Type"="application/json" }

function Parse-Body($content) {
  # JSON 직접 or SSE(data: ...) 둘 다 처리
  if ($content -match '(?m)^data:\s*(.+)$') {
    $lines = [regex]::Matches($content, '(?m)^data:\s*(.+)$') | ForEach-Object { $_.Groups[1].Value }
    return ($lines -join "")
  }
  return $content
}

# 1) initialize
$init = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"ps","version":"1"}}}'
$r = Invoke-WebRequest -Uri $u -Method Post -Body $init -Headers $H -UseBasicParsing -TimeoutSec 30
$sid = $r.Headers["Mcp-Session-Id"]
$H2 = $H.Clone(); $H2["Mcp-Session-Id"] = $sid

# 2) notifications/initialized
$noti = '{"jsonrpc":"2.0","method":"notifications/initialized"}'
try { Invoke-WebRequest -Uri $u -Method Post -Body $noti -Headers $H2 -UseBasicParsing -TimeoutSec 30 | Out-Null } catch {}

# 3) the actual call
$body = "{""jsonrpc"":""2.0"",""id"":2,""method"":""$Method"",""params"":$ParamsJson}"
$resp = Invoke-WebRequest -Uri $u -Method Post -Body $body -Headers $H2 -UseBasicParsing -TimeoutSec 120
Parse-Body $resp.Content