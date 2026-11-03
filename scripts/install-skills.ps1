# Install Prometheus skills so they appear in Claude Code's "/" menu in EVERY project (Windows).
#
#   powershell -ExecutionPolicy Bypass -File scripts\install-skills.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\install-skills.ps1 researcher outlier
#   powershell -ExecutionPolicy Bypass -File scripts\install-skills.ps1 -Project C:\code\my-repo undying
#   powershell -ExecutionPolicy Bypass -File scripts\install-skills.ps1 -Uninstall
param([string]$Project = "", [switch]$Uninstall, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Pick)
$ErrorActionPreference = "Stop"
$Src = Join-Path (Split-Path $PSScriptRoot -Parent) ".claude\skills"
$Dest = if ($Project) { Join-Path (Resolve-Path $Project) ".claude\skills" } else { Join-Path $HOME ".claude\skills" }
$All = "researcher-prometheus","undying-prometheus","suggester-prometheus","outlier-prometheus","planner-prometheus","prometheus","prometheus-daily"
$Blocks = $All[0..4]
function Resolve-Name($n) { if ($n -in "prometheus","prometheus-daily" -or $n -like "*-prometheus") { $n } else { "$n-prometheus" } }
$Skills = if (-not $Pick) { $All } else { $Pick | ForEach-Object { Resolve-Name $_ } }
if (-not $Uninstall -and ($Skills | Where-Object { $_ -in "prometheus","prometheus-daily" })) {
  $Skills = @($Skills) + ($Blocks | Where-Object { $_ -notin $Skills })
}
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
foreach ($s in $Skills) {
  if (-not (Test-Path (Join-Path $Src $s))) { throw "unknown skill: $s" }
  $target = Join-Path $Dest $s
  if (Test-Path $target) { Remove-Item -Recurse -Force $target }
  if ($Uninstall) { Write-Host "removed  /$s" } else { Copy-Item -Recurse (Join-Path $Src $s) $target; Write-Host "installed /$s -> $target" }
}
if (-not $Uninstall) { Write-Host "Done. Restart Claude Code (or open a new session), then type / to see them." }
