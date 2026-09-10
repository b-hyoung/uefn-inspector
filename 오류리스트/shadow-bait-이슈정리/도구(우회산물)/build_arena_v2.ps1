# build_arena_v2.ps1 - Shadow Bait arena builder v2 (backstage/concert theme, larger, visualized)
# English comments only (PS5.1 reads .ps1 as ANSI; Korean breaks the parser).
param([Parameter(Mandatory=$true)][ValidateSet("A","B","C","D")][string]$Id)
$ErrorActionPreference="Continue"
$sp = $PSScriptRoot
$uecall = Join-Path $sp "uecall.ps1"
$STATE = Join-Path $sp "..\state"
if(-not (Test-Path $STATE)){ New-Item -ItemType Directory -Force -Path $STATE | Out-Null }

# ---- asset paths ----
$P = @{
  roadL   = "/Game/Playgrounds/Items/Props/Concert_RoadCase_Lrg.Concert_RoadCase_Lrg_C"
  roadM   = "/Game/Playgrounds/Items/Props/Concert_RoadCase_Med.Concert_RoadCase_Med_C"
  roadS   = "/Game/Playgrounds/Items/Props/Concert_RoadCase_Sml.Concert_RoadCase_Sml_C"
  spkTower= "/Game/Playgrounds/Items/Props/Concert_Speakers_Tower.Concert_Speakers_Tower_C"
  spkLarge= "/Game/Playgrounds/Items/Props/Concert_Speakers_Large.Concert_Speakers_Large_C"
  spkCab  = "/Game/Playgrounds/Items/Props/Concert_Speakers_Cab.Concert_Speakers_Cab_C"
  spkMed  = "/Game/Playgrounds/Items/Props/Concert_Speakers_CabMed.Concert_Speakers_CabMed_C"
  scafCube= "/Game/Playgrounds/Items/Props/Concert_Scaffolding_Cube.Concert_Scaffolding_Cube_C"
  scafRect= "/Game/Playgrounds/Items/Props/Concert_Scaffolding_Rectangle.Concert_Scaffolding_Rectangle_C"
  stage1  = "/Game/Playgrounds/Items/Props/Concert_StageBase_01.Concert_StageBase_01_C"
  stage2  = "/Game/Playgrounds/Items/Props/Concert_StageBase_02.Concert_StageBase_02_C"
  table   = "/Game/Playgrounds/Items/Props/Concert_Table.Concert_Table_C"
  djdesk  = "/Game/Playgrounds/Items/Props/Concert_Dj_Desk.Concert_Dj_Desk_C"
}
$SPOT = @{
  purple="/Game/Playgrounds/Items/Props/Concert_Spotlights_x1_Purple.Concert_Spotlights_x1_Purple_C"
  blue  ="/Game/Playgrounds/Items/Props/Concert_Spotlights_x1_Blue.Concert_Spotlights_x1_Blue_C"
  red   ="/Game/Playgrounds/Items/Props/Concert_Spotlights_x1_Red.Concert_Spotlights_x1_Red_C"
  teal  ="/Game/Playgrounds/Items/Props/Concert_Spotlights_x1_Teal.Concert_Spotlights_x1_Teal_C"
  green ="/Game/Playgrounds/Items/Props/Concert_Spotlights_x1_Green.Concert_Spotlights_x1_Green_C"
  orange="/Game/Playgrounds/Items/Props/Concert_Spotlights_x1_Orange.Concert_Spotlights_x1_Orange_C"
}
$A_GUARD="/CRD_HenchmanSpawner/SetupAssets/PID_Device_GuardSpawner_V2.PID_Device_GuardSpawner_V2"
$A_LIGHT="/CRD_PointLight/SetupAssets/PID_Device_PointLight.PID_Device_PointLight"
$A_SWITCH="/CRD_Switch/SetupAssets/PID_Device_Switch.PID_Device_Switch"
$A_AUDIO="/CRD_AudioPlayer/SetupAssets/PID_CP_Devices_CRD_AudioPlayer.PID_CP_Devices_CRD_AudioPlayer"
$A_SPAWN="/CRD_PlayerSpawn/ItemDefinitions/PID_Device_PlayerSpawnPad.PID_Device_PlayerSpawnPad"

# ---- arena spec (v2: bigger) ----
$spec = switch($Id){
 "A" { @{ cx=-30000; cy=30000; half=2600; lure=$false; sw=$false; tint="teal";   theme="plain" } }
 "B" { @{ cx=0;      cy=30000; half=2600; lure=$true;  sw=$true;  tint="purple"; theme="plain" } }
 "C" { @{ cx=30000;  cy=30000; half=2600; lure=$true;  sw=$true;  tint="red";    theme="maze"  } }
 "D" { @{ cx=60000;  cy=30000; half=4200; lure=$true;  sw=$true;  tint="blue";   theme="open"  } }
}
if($spec -is [array]){ $spec=$spec[0] }
$cx=[int](@($spec.cx)[0]); $cy=[int](@($spec.cy)[0]); $H=[int](@($spec.half)[0])
$WH=[int]700                    # wall height (taller = better enclosure)
$SPAN=[int]($H*2); $EDGE=[int]($H-30); $HZ=[int]($WH/2); $SPANI=[int]($H*2-120)
$tint=[string](@($spec.tint)[0]); $theme=[string](@($spec.theme)[0])
$lure=[bool](@($spec.lure)[0]); $swOn=[bool](@($spec.sw)[0])

$log = New-Object System.Collections.ArrayList
Write-Host "===== ARENA $Id v2  center($cx,$cy) half=$H theme=$theme tint=$tint ====="

function Post($json){ (& $uecall -Method "tools/call" -ParamsJson $json | Out-String) }
function RefOf($t){ if($t -match '"refPath\\?"\s*:\s*\\?"([^"\\]+)'){ return $Matches[1] } return $null }

# stop game if running
$t = Post (@{name="call_tool";arguments=@{toolset_name="ValkyrieToolset.SessionToolset";tool_name="GetGameState";arguments=@{}}} | ConvertTo-Json -Depth 20 -Compress)
if($t -match "Running"){ Post (@{name="call_tool";arguments=@{toolset_name="ValkyrieToolset.SessionToolset";tool_name="StopGame";arguments=@{}}} | ConvertTo-Json -Depth 20 -Compress) | Out-Null; Start-Sleep 5 }

# ---- 1) geo parent + floor/walls ----
$t = Post (@{name="call_tool";arguments=@{toolset_name="editor_toolset.toolsets.scene.SceneTools";tool_name="add_to_scene_from_class";arguments=@{actor_type=@{refPath="/Script/Engine.Actor"};name="ArenaV2$($Id)_Geo";xform=@{location=@{x=[double]$cx;y=[double]$cy;z=0.0}}}}} | ConvertTo-Json -Depth 20 -Compress)
$geo = RefOf $t
if(-not $geo){ Write-Host "GEO FAIL"; exit 1 }
[void]$log.Add(@{label="geo";ref=$geo}); Write-Host "  geo ok"

$cubes = New-Object System.Collections.ArrayList
[void]$cubes.Add(@{n="floor";d=@($SPAN,$SPAN,60);   p=@(0,0,-30)})
[void]$cubes.Add(@{n="wallN";d=@($SPAN,60,$WH);     p=@(0,$EDGE,$HZ)})
[void]$cubes.Add(@{n="wallS";d=@($SPAN,60,$WH);     p=@(0,(-1*$EDGE),$HZ)})
[void]$cubes.Add(@{n="wallE";d=@(60,$SPANI,$WH);    p=@($EDGE,0,$HZ)})
[void]$cubes.Add(@{n="wallW";d=@(60,$SPANI,$WH);    p=@((-1*$EDGE),0,$HZ)})
# maze interior walls (C only)
if($theme -eq "maze"){
  $mz = @(@(0,-1300,3400,60),@(0,1300,3400,60),@(-1300,0,60,2100),@(1300,0,60,2100),@(-650,-650,1300,60),@(650,650,1300,60),@(650,-650,60,1300),@(-650,650,60,1300))
  $i=0; foreach($m in $mz){ [void]$cubes.Add(@{n="maze$i";d=@($m[2],$m[3],$WH);p=@($m[0],$m[1],$HZ)}); $i++ }
}
$okC=0
foreach($cb in $cubes){
  $j = @{name="call_tool";arguments=@{toolset_name="editor_toolset.toolsets.primitive.PrimitiveTools";tool_name="add_cube";arguments=@{actor=@{refPath=$geo};name=$cb.n;dimensions=@{x=[double]$cb.d[0];y=[double]$cb.d[1];z=[double]$cb.d[2]};local_transform=@{location=@{x=[double]$cb.p[0];y=[double]$cb.p[1];z=[double]$cb.p[2]}}}}} | ConvertTo-Json -Depth 20 -Compress
  $r = Post $j
  if($r -notmatch '"isError"\s*:\s*true'){ $okC++ }
}
Write-Host "  cubes $okC/$($cubes.Count)"

# ---- 2) props (cover + set dressing) ----
$props = New-Object System.Collections.ArrayList
function AddP($path,$lx,$ly,$lz,$yaw,$tag){ [void]$props.Add(@{a=$path;x=($cx+$lx);y=($cy+$ly);z=$lz;yaw=$yaw;t=$tag}) }

if($theme -eq "maze"){
  # dense cover tucked into maze pockets
  AddP $P.roadL  -1900 -1900 0 0   "cover"
  AddP $P.roadM   1900 -1900 0 37  "cover"
  AddP $P.spkCab -1900  1900 0 74  "cover"
  AddP $P.roadS   1900  1900 0 111 "cover"
  AddP $P.roadL      0 -1900 0 148 "cover"
  AddP $P.roadM      0  1900 0 185 "cover"
  AddP $P.spkCab -1900     0 0 222 "cover"
  AddP $P.roadS   1900     0 0 259 "cover"
  AddP $P.roadL   -650 -1900 0 296 "cover"
  AddP $P.spkMed   650  1900 0 333 "cover"
  AddP $P.scafCube -1300 -1300 0 0  "struct"
  AddP $P.scafCube  1300  1300 0 45 "struct"
} elseif($theme -eq "open"){
  # sparse but tall cover across a big field
  AddP $P.spkTower -2400 -2400 0 0   "cover"
  AddP $P.spkLarge  2400 -2400 0 53  "cover"
  AddP $P.scafRect -2400  2400 0 106 "cover"
  AddP $P.roadL     2400  2400 0 159 "cover"
  AddP $P.spkTower     0     0 0 212 "cover"
  AddP $P.spkLarge -1200  1600 0 265 "cover"
  AddP $P.scafRect  1600 -1200 0 318 "cover"
  AddP $P.stage1       0  2600 0 180 "stage"
} else {
  # baseline: mixed cover ring + center stage
  AddP $P.roadL  -1400 -1400 0 0   "cover"
  AddP $P.spkCab  1400 -1400 0 45  "cover"
  AddP $P.roadM  -1400  1400 0 90  "cover"
  AddP $P.spkMed  1400  1400 0 135 "cover"
  AddP $P.roadL      0  -900 0 180 "cover"
  AddP $P.spkCab     0   900 0 225 "cover"
  AddP $P.roadM   -900     0 0 270 "cover"
  AddP $P.spkMed   900     0 0 315 "cover"
  AddP $P.stage1     0     0 0 0   "stage"
  AddP $P.djdesk     0   260 60 180 "dress"
  AddP $P.scafCube -1900  1900 0 0 "struct"
  AddP $P.scafCube  1900 -1900 0 0 "struct"
}
# corner speaker towers + colored spotlights along walls (visual identity)
$c1=[int]($H-420)
$c1n=[int](-1*$c1)
AddP $P.spkTower $c1n $c1n 0 45  "tower"
AddP $P.spkTower $c1  $c1n 0 315 "tower"
AddP $P.spkTower $c1n $c1  0 135 "tower"
AddP $P.spkTower $c1  $c1  0 225 "tower"
$spotPath = [string]$SPOT[$tint]
$s1=[int]($H-260); $s1n=[int](-1*$s1)
AddP $spotPath $s1n 0    0 90  "spot"
AddP $spotPath $s1  0    0 270 "spot"
AddP $spotPath 0    $s1n 0 0   "spot"
AddP $spotPath 0    $s1  0 180 "spot"

$okP=0; $pi=0
foreach($pr in $props){
  $nm = "V2$($Id)_$($pr.t)_$pi"; $pi++
  $j = @{name="call_tool";arguments=@{toolset_name="editor_toolset.toolsets.scene.SceneTools";tool_name="add_to_scene_from_asset";arguments=@{asset_path=$pr.a;name=$nm;xform=@{location=@{x=[double]$pr.x;y=[double]$pr.y;z=[double]$pr.z};rotation=@{pitch=0.0;yaw=[double]$pr.yaw;roll=0.0}};snap_to_ground=$false}}} | ConvertTo-Json -Depth 20 -Compress
  $r = Post $j
  $ref = RefOf $r
  if($ref){ [void]$log.Add(@{label="prop_$($pr.t)";ref=$ref}); $okP++ } else { Write-Host "    ! $nm : $($r -replace '\s+',' ' | ForEach-Object { $_.Substring(0,[Math]::Min(160,$_.Length)) })" }
}
Write-Host "  props $okP/$($props.Count)"

# ---- 3) devices ----
$lightOffsets = if($theme -eq "maze"){ @(@(-1900,-1900),@(0,-1900),@(1900,-1900),@(-1900,0),@(0,0),@(1900,0),@(-1900,1900),@(0,1900),@(1900,1900),@(650,-650)) }
                elseif($theme -eq "open"){ @(@(-2600,-2600),@(2600,-2600),@(-2600,2600),@(2600,2600)) }
                else { @(@(-1600,-1600),@(1600,-1600),@(-1600,1600),@(1600,1600),@(0,0),@(0,-2000)) }
$devs = New-Object System.Collections.ArrayList
[void]$devs.Add(@{a=$A_SPAWN;x=$cx-$H+400;y=$cy-$H+400;z=100;l="spawn"})
[void]$devs.Add(@{a=$A_GUARD;x=$cx+$H-400;y=$cy+$H-400;z=100;l="guard"})
$i=0; foreach($L in $lightOffsets){ [void]$devs.Add(@{a=$A_LIGHT;x=$cx+$L[0];y=$cy+$L[1];z=500;l="light$i"}); $i++ }
if($swOn){ [void]$devs.Add(@{a=$A_SWITCH;x=$cx-500;y=$cy-$H+450;z=100;l="lightsw0"}); [void]$devs.Add(@{a=$A_SWITCH;x=$cx+500;y=$cy+$H-450;z=100;l="lightsw1"}) }
if($lure){ [void]$devs.Add(@{a=$A_AUDIO;x=$cx+$H-600;y=$cy-$H+600;z=150;l="decoyaudio"}); [void]$devs.Add(@{a=$A_SWITCH;x=$cx-$H+700;y=$cy;z=100;l="luresw0"}); [void]$devs.Add(@{a=$A_SWITCH;x=$cx;y=$cy-700;z=100;l="luresw1"}) }

$refs=@{}
foreach($d in $devs){
  $j = @{name="call_tool";arguments=@{toolset_name="ValkyrieToolset.DeviceToolset";tool_name="PlaceDevice";arguments=@{assetPath=@{refPath=$d.a};transform=@{location=@{x=[double]$d.x;y=[double]$d.y;z=[double]$d.z}}}}} | ConvertTo-Json -Depth 20 -Compress
  $r = Post $j
  $ref = RefOf $r
  if($ref){ $refs[$d.l]=$ref; [void]$log.Add(@{label=$d.l;ref=$ref;x=$d.x;y=$d.y}) }
}
Write-Host "  devices $($refs.Count)/$($devs.Count)"

# ---- 4) bindings ----
function Bind($s,$e,$tg,$f){ Post (@{name="call_tool";arguments=@{toolset_name="ValkyrieToolset.DeviceToolset";tool_name="AddEventBinding";arguments=@{sourceDevicePath=@{refPath=$s};sourceEvent=$e;targetDevicePath=@{refPath=$tg};targetFunction=$f}}} | ConvertTo-Json -Depth 20 -Compress) | Out-Null }
if($swOn){
  $lk = @($refs.Keys | Where-Object { $_ -like "light*" -and $_ -notlike "lightsw*" })
  $halfN=[math]::Ceiling($lk.Count/2); $j=0; $nb=0
  foreach($k in $lk){ $swk = if($j -lt $halfN){"lightsw0"}else{"lightsw1"}; if($refs.ContainsKey($swk)){ Bind $refs[$swk] "On Turned On" $refs[$k] "Turn Off"; Bind $refs[$swk] "On Turned Off" $refs[$k] "Turn On"; $nb+=2 }; $j++ }
  Write-Host "  light bindings $nb"
}
if($lure -and $refs.ContainsKey("decoyaudio")){
  $nb=0; foreach($l in @("luresw0","luresw1")){ if($refs.ContainsKey($l)){ Bind $refs[$l] "On Turned On" $refs["decoyaudio"] "Play"; Bind $refs[$l] "On Turned Off" $refs["decoyaudio"] "Play"; $nb+=2 } }
  Write-Host "  lure bindings $nb"
}

# ---- 5) save all ----
$okS=0
foreach($it in $log){ $r = Post (@{name="call_tool";arguments=@{toolset_name="editor_toolset.toolsets.scene.SceneTools";tool_name="save_actor";arguments=@{actor=@{refPath=$it.ref}}}} | ConvertTo-Json -Depth 20 -Compress); if($r -notmatch '"isError"\s*:\s*true'){$okS++} }
Write-Host "  saved $okS/$($log.Count)"

$log | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $STATE "arenaV2_$Id.json") -Encoding utf8
Write-Host "DONE arena $Id v2 - total $($log.Count) actors"