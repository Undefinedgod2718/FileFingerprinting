param(
    [Parameter(Mandatory = $true)]
    [string]$LegacyCoreSource,
    [string]$Configuration = "Release",
    [string]$OutputDir = "$PSScriptRoot\..\publish"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path "$PSScriptRoot\.."
$staging = Join-Path $OutputDir "installer-staging"
$runtimeDest = Join-Path $staging "runtime\LegacyCore.exe"
$iss = Join-Path $root "tools/installer/FileFingerprinting.iss"
$installerOut = Join-Path $OutputDir "installer"

if (-not (Test-Path $LegacyCoreSource)) {
    throw "LegacyCoreSource not found: $LegacyCoreSource"
}

Write-Host "Cleaning publish/installer artifacts ..."
Get-Process -Name "FileFingerprinting" -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
    (Join-Path $OutputDir "installer-staging"), `
    (Join-Path $OutputDir "installer"), `
    (Join-Path $OutputDir "app-multifile")
Push-Location $root
try {
    dotnet clean -c $Configuration 2>&1 | Out-Null
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
        "src\TpFileM.App\bin", "src\TpFileM.App\obj"
}
finally {
    Pop-Location
}

Write-Host "Publishing installer staging ..."
& (Join-Path $root "tools/publish.ps1") -Configuration $Configuration -OutputDir $OutputDir -ForInstaller

& (Join-Path $root "tools/installer/prepare-wizard-assets.ps1")

New-Item -ItemType Directory -Force -Path (Split-Path $runtimeDest) | Out-Null
Copy-Item $LegacyCoreSource $runtimeDest -Force
Write-Host "Copied legacy core -> $runtimeDest"

$iscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
    throw "Inno Setup 6 not found. Install from https://jrsoftware.org/isinfo.php then re-run."
}

New-Item -ItemType Directory -Force -Path $installerOut | Out-Null
& $iscc "/DStagingDir=$staging" "/DOutputDir=$installerOut" $iss

$setup = Get-ChildItem $installerOut -Filter "FileFingerprinting-Setup*.exe" | Select-Object -First 1
if ($setup) {
    Write-Host "Installer: $($setup.FullName)"
}
else {
    throw "ISCC finished but setup exe not found in $installerOut"
}
