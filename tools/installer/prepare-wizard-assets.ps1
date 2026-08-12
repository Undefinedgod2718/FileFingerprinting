param(
    [string]$IcoPath = "$PSScriptRoot\..\..\src\TpFileM.App\Assets\logo.ico",
    [string]$OutBmp = "$PSScriptRoot\assets\wizard_small.bmp"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$icoPathResolved = Resolve-Path $IcoPath
$outDir = Split-Path $OutBmp -Parent
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$icon = New-Object System.Drawing.Icon($icoPathResolved.Path)
$size = 55
$height = 58
$bmp = New-Object System.Drawing.Bitmap $size, $height
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.Clear([System.Drawing.Color]::FromArgb(255, 139, 139, 139))
$destRect = New-Object System.Drawing.Rectangle 0, 0, $size, $height
$graphics.DrawIcon($icon, $destRect)
$graphics.Dispose()
$icon.Dispose()

$bmp.Save($OutBmp, [System.Drawing.Imaging.ImageFormat]::Bmp)
$bmp.Dispose()

Write-Host "Wizard asset: $OutBmp"
