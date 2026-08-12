param(
    [string]$GoldenPath = "$PSScriptRoot\fixtures\legacy-golden.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$golden = Get-Content $GoldenPath -Raw | ConvertFrom-Json
$repo = Resolve-Path "$PSScriptRoot\.."
$legacy = "D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe"
$modern = Join-Path $repo "publish\app\FileFingerprinting.exe"

Write-Host "=== TPFileM manual parity helper ===" -ForegroundColor Cyan
Write-Host "Legacy : $legacy"
Write-Host "Modern : $modern"
Write-Host ""

foreach ($v in $golden.vectors) {
    $label = if ($v.path) { $v.file + " @ " + $v.path } else { $v.file }
    Write-Host $label -ForegroundColor Yellow
    Write-Host "  CRC: $($v.crc)"
    if ($v.sha) { Write-Host "  SHA: $($v.sha)" }
    $fixture = Join-Path $repo "tools\fixtures\$($v.file)"
    if (Test-Path $fixture) { Write-Host "  path: $fixture" }
    elseif ($v.path -and (Test-Path $v.path)) { Write-Host "  path: $($v.path)" }
    Write-Host ""
}

$shotDir = Join-Path $repo "tools\fixtures\screenshots\phase1"
New-Item -ItemType Directory -Force -Path $shotDir | Out-Null
Write-Host "Screenshots -> $shotDir"
Write-Host "See wiki/testing/manual-gui-parity.md"

if (Test-Path $legacy) { Start-Process $legacy }
if (Test-Path $modern) { Start-Process $modern }
