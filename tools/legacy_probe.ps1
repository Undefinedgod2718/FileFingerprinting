param(
    [string]$LegacyExe = "D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe",
    [string]$FixtureDir = "$PSScriptRoot\fixtures",
    [string]$ModernDll = "$PSScriptRoot\..\src\TpFileM.Core\bin\Debug\net10.0\TpFileM.Core.dll"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $FixtureDir | Out-Null

$fixtures = @{
    "empty.bin" = [byte[]]@()
    "test.bin" = [System.Text.Encoding]::ASCII.GetBytes("test")
    "seq16.bin" = [byte[]](0..15)
    "digits.bin" = [System.Text.Encoding]::ASCII.GetBytes("123456789")
}

$vectors = @()
foreach ($name in $fixtures.Keys) {
    $path = Join-Path $FixtureDir $name
    [IO.File]::WriteAllBytes($path, $fixtures[$name])
    $vectors += [pscustomobject]@{ file = $name; path = $path; size = $fixtures[$name].Length }
}

Write-Host "Fixtures written to $FixtureDir"
$vectors | Format-Table -AutoSize

if (-not (Test-Path $LegacyExe)) {
    Write-Warning "Legacy exe not found: $LegacyExe"
    exit 1
}

Write-Host "`nLegacy binary: $LegacyExe"
Write-Host "Size: $((Get-Item $LegacyExe).Length) bytes"
Write-Host "`nRun modern parity check:"
Write-Host "  dotnet test tests/TpFileM.Core.Tests"
Write-Host "`nManual legacy check: launch $LegacyExe, select each fixture, click Generate Key, compare CRC/SHA fields."

# Optional: invoke modern core via dotnet script if built
if (Test-Path $ModernDll) {
    Write-Host "`nModern DLL present: $ModernDll"
}

$out = Join-Path $FixtureDir "vectors.json"
$vectors | ConvertTo-Json | Set-Content -Path $out -Encoding UTF8
Write-Host "Wrote $out"
