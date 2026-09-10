# Install the uefn-* slash skills into ~/.claude/skills (Windows PowerShell)
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$src  = Join-Path $root "game-loop-kit\skills"
$kit  = Join-Path $root "game-loop-kit"
$dest = Join-Path $env:USERPROFILE ".claude\skills"

New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($s in @("uefn-game-loop","uefn-intake","uefn-level","uefn-review")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $dest $s) | Out-Null
    (Get-Content (Join-Path $src "$s\SKILL.md") -Raw) `
        -replace '(?m)^\*\*KIT\*\* = .*', "**KIT** = ``$kit``" |
        Set-Content (Join-Path $dest "$s\SKILL.md") -Encoding utf8
    Write-Output "installed: /$s"
}
Write-Output ""
Write-Output "done -> $dest"
Write-Output "restart Claude Code (or open a new session) to load them."
