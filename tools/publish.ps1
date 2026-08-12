param(
    [string]$Configuration = "Release",
    [string]$OutputDir = "$PSScriptRoot\..\publish",
    [switch]$ForInstaller
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path "$PSScriptRoot\.."
Push-Location $root

try {
    dotnet test -c $Configuration --no-restore 2>$null
    if ($LASTEXITCODE -ne 0) {
        dotnet restore
        dotnet test -c $Configuration
    }

    $cliPublish = Join-Path $root "src/TpFileM.LegacySha.Cli/bin/$Configuration/net10.0/win-x86/publish"
    dotnet publish src/TpFileM.LegacySha.Cli/TpFileM.LegacySha.Cli.csproj -c $Configuration -r win-x86 --self-contained true -p:PublishSingleFile=true -o $cliPublish

    $cliExe = Join-Path $cliPublish "TpFileM.LegacySha.Cli.exe"

    if ($ForInstaller) {
        $staging = Join-Path $OutputDir "installer-staging"
        $runtimeDir = Join-Path $staging "runtime"
        New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

        dotnet publish src/TpFileM.App/TpFileM.App.csproj `
            -c $Configuration `
            -r win-x64 `
            --self-contained `
            -p:PublishSingleFile=false `
            -o $staging

        Copy-Item $cliExe (Join-Path $staging "TpFileM.LegacySha.Cli.exe") -Force

        Write-Host "Installer staging: $staging"
        Write-Host "Next: .\tools\build-installer.ps1 -LegacyCoreSource <path-to-legacy-exe>"
        Get-ChildItem $staging -Recurse -File | Format-Table FullName, Length -AutoSize
        return
    }

    $appOut = Join-Path $OutputDir "app"
    $mcpOut = Join-Path $OutputDir "mcp"
    New-Item -ItemType Directory -Force -Path $appOut, $mcpOut | Out-Null

    dotnet publish src/TpFileM.App/TpFileM.App.csproj `
        -c $Configuration `
        -r win-x64 `
        --self-contained `
        -p:PublishSingleFile=false `
        -o $appOut

    dotnet publish src/TpFileM.Mcp/TpFileM.Mcp.csproj `
        -c $Configuration `
        -r win-x64 `
        --self-contained `
        -p:PublishSingleFile=true `
        -o $mcpOut

    Copy-Item (Join-Path $mcpOut "TpFileM.Mcp.exe") (Join-Path $appOut "TpFileM.Mcp.exe") -Force
    Copy-Item $cliExe (Join-Path $appOut "TpFileM.LegacySha.Cli.exe") -Force
    Copy-Item $cliExe (Join-Path $mcpOut "TpFileM.LegacySha.Cli.exe") -Force

    $guiExe = Join-Path $appOut "FileFingerprinting.exe"

    @"
File Fingerprinting — developer publish output
==============================================

GUI:  $guiExe
MCP:  $appOut\TpFileM.Mcp.exe  (also copied next to GUI)
SHA:  $appOut\TpFileM.LegacySha.Cli.exe  (win-x86 legacy SHA helper)

End-user installer: see wiki/dev/ — run publish.ps1 -ForInstaller then build-installer.ps1

Cursor mcp.json example:
{
  "mcpServers": {
    "tpfilem": {
      "command": "$($appOut.Replace('\','/'))/TpFileM.Mcp.exe",
      "args": []
    }
  }
}
"@ | Set-Content -Path (Join-Path $OutputDir "README-publish.txt") -Encoding UTF8

    Write-Host "Published to $OutputDir"
    Get-ChildItem $appOut -Filter *.exe | Format-Table Name, Length -AutoSize
}
finally {
    Pop-Location
}
