# uefn_gui.ps1 — UEFN GUI 자동화 헬퍼 (스크린샷 → 좌표 클릭). 검증 2026-09-14: 새 프로젝트 생성 end-to-end.
# 함정: (1) 150% 배율 모니터 → SetProcessDPIAware 필수(아래서 호출) (2) 프로젝트 브라우저는 별도 톱레벨 창
#       (3) 한글 IME → SendKeys 영문이 자모로 들어감. 이름은 클립보드(^v)로. (4) 좌표는 머신별 → state/env.md에 기록
# 절차는 loop/recover.md 절차 D. 대상 창은 Uefn-Main(가장 큰 창) 기준 상대 좌표(물리 px).
# UEFN GUI automation helper (screenshot-driven). Usage:
#   . .\uefn_gui.ps1 ; Uefn-Wait 240 ; Uefn-Shot shot1.png ; Uefn-Click 1200 700 ; Uefn-Type "Name" ; Uefn-Key "{ENTER}"
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
if (-not ("Win32U" -as [type])) {
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Text;
public class Win32U {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  public delegate bool EnumProc(IntPtr h, IntPtr l);
}
"@
}
# 150% monitors: make this process DPI-aware so GetWindowRect / SetCursorPos / CopyFromScreen all use physical pixels
[Win32U]::SetProcessDPIAware() | Out-Null
$script:OUT = Join-Path $env:TEMP "uefn_gui_shots"
New-Item -ItemType Directory -Force $script:OUT | Out-Null

function Uefn-Windows {
  # all visible top-level windows of UnrealEditorFortnite with title
  $procs = Get-Process -Name UnrealEditorFortnite* -ErrorAction SilentlyContinue
  if (-not $procs) { return @() }
  $pids = @($procs | ForEach-Object { [uint32]$_.Id })
  $found = New-Object System.Collections.ArrayList
  $cb = [Win32U+EnumProc]{ param($h, $l)
    [uint32]$wpid = 0; [Win32U]::GetWindowThreadProcessId($h, [ref]$wpid) | Out-Null
    if ($pids -contains $wpid -and [Win32U]::IsWindowVisible($h)) {
      $sb = New-Object System.Text.StringBuilder 512; [Win32U]::GetWindowText($h, $sb, 512) | Out-Null
      $r = New-Object Win32U+RECT; [Win32U]::GetWindowRect($h, [ref]$r) | Out-Null
      $w = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
      if ($w -gt 200 -and $ht -gt 200) { [void]$found.Add([pscustomobject]@{ H=$h; Title=$sb.ToString(); L=$r.Left; T=$r.Top; W=$w; Ht=$ht }) }
    }
    return $true }
  [Win32U]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
  if ($found.Count -eq 0) {
    foreach ($p in $procs) {
      $h = $p.MainWindowHandle
      if ($h -ne [IntPtr]::Zero) {
        $r = New-Object Win32U+RECT; [Win32U]::GetWindowRect($h, [ref]$r) | Out-Null
        [void]$found.Add([pscustomobject]@{ H=$h; Title=$p.MainWindowTitle; L=$r.Left; T=$r.Top; W=($r.Right-$r.Left); Ht=($r.Bottom-$r.Top) })
      }
    }
  }
  return @($found)
}

function Uefn-Wait([int]$seconds = 240) {
  $t0 = Get-Date
  while (((Get-Date) - $t0).TotalSeconds -lt $seconds) {
    $w = Uefn-Windows
    if ($w.Count -gt 0) { return $w }
    Start-Sleep -Seconds 5
  }
  return @()
}

function Uefn-Main {
  $w = Uefn-Windows | Sort-Object { $_.W * $_.Ht } -Descending | Select-Object -First 1
  return $w
}

function Uefn-Shot([string]$name = "shot.png", [double]$scale = 0.5) {
  $w = Uefn-Main
  if (-not $w) { throw "no UEFN window" }
  [Win32U]::ShowWindow($w.H, 9) | Out-Null; [Win32U]::SetForegroundWindow($w.H) | Out-Null; Start-Sleep -Milliseconds 400
  $r = New-Object Win32U+RECT; [Win32U]::GetWindowRect($w.H, [ref]$r) | Out-Null
  $wd = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
  $bmp = New-Object System.Drawing.Bitmap $wd, $ht
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($r.Left, $r.Top, 0, 0, $bmp.Size); $g.Dispose()
  $sw = [int]($wd * $scale); $sh = [int]($ht * $scale)
  $small = New-Object System.Drawing.Bitmap $bmp, $sw, $sh
  $path = Join-Path $script:OUT $name; $small.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose(); $small.Dispose()
  "$path  window=($($r.Left),$($r.Top)) size=${wd}x${ht} scale=$scale title='$($w.Title)'"
}

# x,y are WINDOW-relative coords at FULL resolution (multiply screenshot coords by 1/scale)
function Uefn-Click([int]$x, [int]$y, [switch]$Double, [switch]$Right) {
  $w = Uefn-Main; if (-not $w) { throw "no UEFN window" }
  # 최소화된 창은 rect가 (-32000,-32000) -> 복원 후 rect를 다시 읽는다(실측 함정)
  [Win32U]::ShowWindow($w.H, 9) | Out-Null; Start-Sleep -Milliseconds 400
  $r = New-Object Win32U+RECT; [Win32U]::GetWindowRect($w.H, [ref]$r) | Out-Null
  if ($r.Left -le -30000 -or $r.Top -le -30000) { throw "window is minimized/offscreen ($($r.Left),$($r.Top)) - restore it first" }
  $ax = $r.Left + $x; $ay = $r.Top + $y
  [Win32U]::SetForegroundWindow($w.H) | Out-Null; Start-Sleep -Milliseconds 200
  [Win32U]::SetCursorPos($ax, $ay) | Out-Null; Start-Sleep -Milliseconds 150
  $down = 0x0002; $up = 0x0004; if ($Right) { $down = 0x0008; $up = 0x0010 }
  [Win32U]::mouse_event($down,0,0,0,[UIntPtr]::Zero); [Win32U]::mouse_event($up,0,0,0,[UIntPtr]::Zero)
  if ($Double) { Start-Sleep -Milliseconds 90; [Win32U]::mouse_event($down,0,0,0,[UIntPtr]::Zero); [Win32U]::mouse_event($up,0,0,0,[UIntPtr]::Zero) }
  "clicked abs=($ax,$ay) rel=($x,$y) double=$Double"
}

function Uefn-Type([string]$text) {
  $w = Uefn-Main; [Win32U]::SetForegroundWindow($w.H) | Out-Null; Start-Sleep -Milliseconds 200
  [System.Windows.Forms.SendKeys]::SendWait($text); "typed: $text"
}
function Uefn-Key([string]$keys) { $w = Uefn-Main; [Win32U]::SetForegroundWindow($w.H) | Out-Null; Start-Sleep -Milliseconds 200; [System.Windows.Forms.SendKeys]::SendWait($keys); "keys: $keys" }
function Uefn-Projects { Get-ChildItem "$env:USERPROFILE\Documents\Fortnite Projects" -Directory | Select-Object Name, LastWriteTime }

function Uefn-Wheel([int]$x,[int]$y,[int]$notches){
  $w = Uefn-Main; [Win32U]::ShowWindow($w.H, 9) | Out-Null; Start-Sleep -Milliseconds 300
  $r = New-Object Win32U+RECT; [Win32U]::GetWindowRect($w.H,[ref]$r) | Out-Null
  [Win32U]::SetCursorPos($r.Left+$x,$r.Top+$y) | Out-Null; Start-Sleep -Milliseconds 150
  for($i=0;$i -lt [Math]::Abs($notches);$i++){ $d = if($notches -lt 0){[uint32]4294967176}else{[uint32]120}; [Win32U]::mouse_event(0x0800,0,0,$d,[UIntPtr]::Zero); Start-Sleep -Milliseconds 120 }
}
function Uefn-Launch {
  # 런처 URI로 UEFN 기동(exe 직접은 1회용 exchange code라 불가). 프로세스 등장까지 대기.
  if (Get-Process -Name UnrealEditorFortnite* -ErrorAction SilentlyContinue) { return "already running" }
  Start-Process "com.epicgames.launcher://apps/fn%3A1e8bda5cfbb641b9a9aea8bd62285f73%3AFortnite_Studio?action=launch&silent=true"
  $t0 = Get-Date; do { Start-Sleep -Seconds 5 } while (-not (Get-Process -Name UnrealEditorFortnite* -ErrorAction SilentlyContinue) -and ((Get-Date)-$t0).TotalSeconds -lt 120)
  "launched"
}
# 검증된 시퀀스(이 머신, 창 2291x1623 기준 상대 좌표). 다른 머신은 스크린샷으로 좌표를 다시 잡는다.
#   Uefn-Launch; Uefn-Wait 270; Uefn-Shot home.png 0.4
#   Uefn-Click 220 362          # 새 프로젝트 → 프로젝트 브라우저(별창) 열림, 기본 템플릿 '심플'
#   (템플릿 선택: 그리드 첫 칸 780,475 / 휠 스크롤 Uefn-Wheel 1025 750 -5)
#   Uefn-Click 1932 1337        # 생성 → Documents\Fortnite Projects\<이름> 생성(~10s), 에디터 로드(~40s)
#   이름 변경(❓미안정): Set-Clipboard "이름"; Uefn-Click 1737 1230; Uefn-Key "{END}{BS 30}"; Uefn-Key "^v"

function Uefn-CloseEditor([int]$graceSeconds = 20) {
  # 새 프로젝트/저장 완료 상태에서만 쓴다. WM_CLOSE 후 남으면 강제 종료.
  $p = Get-Process -Name UnrealEditorFortnite* -ErrorAction SilentlyContinue
  if (-not $p) { return "not running" }
  $p | ForEach-Object { $_.CloseMainWindow() | Out-Null }
  $t0 = Get-Date; while ((Get-Process -Name UnrealEditorFortnite* -ErrorAction SilentlyContinue) -and ((Get-Date)-$t0).TotalSeconds -lt $graceSeconds) { Start-Sleep -Seconds 2 }
  if (Get-Process -Name UnrealEditorFortnite* -ErrorAction SilentlyContinue) { Stop-Process -Name UnrealEditorFortnite* -Force; Start-Sleep -Seconds 3; return "killed" }
  "closed"
}

function Uefn-EnableProjectFlags([string]$uefnproject) {
  # unreal-mcp(:8000)·에디터 Python이 뜨도록 experimental 플래그를 넣는다. 에디터가 닫힌 상태에서만.
  if (Get-Process -Name UnrealEditorFortnite* -ErrorAction SilentlyContinue) { throw "close the editor first" }
  $raw = Get-Content $uefnproject -Raw -Encoding UTF8
  $j = $raw | ConvertFrom-Json
  if (-not $j.dataSets) { $j | Add-Member -NotePropertyName dataSets -NotePropertyValue ([pscustomobject]@{}) }
  if (-not $j.dataSets.experimental) { $j.dataSets | Add-Member -NotePropertyName experimental -NotePropertyValue ([pscustomobject]@{ version = 1 }) }
  $e = $j.dataSets.experimental
  if (-not $e.pythonExperimental) { $e | Add-Member -NotePropertyName pythonExperimental -NotePropertyValue ([pscustomobject]@{ bEnablePythonForProject = $true }) } else { $e.pythonExperimental.bEnablePythonForProject = $true }
  if (-not $e.toolsets) { $e | Add-Member -NotePropertyName toolsets -NotePropertyValue ([pscustomobject]@{ bEnableToolsetsForProject = $true }) } else { $e.toolsets.bEnableToolsetsForProject = $true }
  Copy-Item $uefnproject "$uefnproject.bak" -Force
  ($j | ConvertTo-Json -Depth 12) | Set-Content $uefnproject -Encoding UTF8
  "flags set (backup: $uefnproject.bak)"
}

function Uefn-PortOpen([int]$port) { $c = New-Object Net.Sockets.TcpClient; try { $c.Connect('127.0.0.1',$port); $true } catch { $false } finally { $c.Dispose() } }
