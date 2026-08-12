# Release 1.0.1

**Status:** Verified (2026-07-07) — shipped after startup fixes, installer packaging, and Minecraft UI polish.

Product: **File Fingerprinting** / 文件指紋識別  
Installer: `publish/installer/FileFingerprinting-Setup.exe` (`AppVersion=1.0.1`)  
Dev publish: `publish/app/` (multi-file; run `FileFingerprinting.exe` from this folder)

## What changed from 1.0.0

| Area | Change |
|------|--------|
| **Version** | `AppVersion`, assembly `Version` / `FileVersion` → **1.0.1** |
| **Publish** | GUI `PublishSingleFile=false` — ship full folder (~260 files), not lone ~140 MB exe |
| **Installer** | Inno Setup copies entire `installer-staging` tree (`recursesubdirs`) |
| **Localization** | `strings-en.json`, `strings-zh-TW.json` embedded (no `.en.` culture suffix) |
| **UI** | Minecraft pixel theme: tiled textures, Monocraft font, stone buttons, spruce Key Mode, emerald progress, left-column field labels |
| **Branding** | `FileFingerprinting.exe`, window title File Fingerprinting |

## Defects fixed in 1.0.1

All logged in [bug-reports.md](bug-reports.md):

| ID | Summary | Fixed in |
|----|---------|----------|
| FF-001 | Startup `JsonException` (`0xEF`) — localization resource names | 1.0.1 |
| FF-002 | Single-file publish crash (`0xE0434352`) | 1.0.1 |
| FF-003 | Installer shipped only 3 files (missing runtime DLLs) | 1.0.1 |
| FF-004 | Crafting-grid buttons unreadable (reverted to stone) | 1.0.1 |
| FF-005 | Stale `publish/app` or partial copy shows old UI | 1.0.1 (process) |
| FF-006 | Missing visible field labels (File name / CRC / SHA) | 1.0.1 |
| FF-007 | Key Mode combo low contrast (wrong texture/size) | 1.0.1 |
| FF-008 | Title truncation + footer squeeze at 680×440; yellow tooltips hard to read | 1.0.1 |

## UI theme (1.0.1)

See [ui-design.md](../implementation/ui-design.md). Highlights:

- Native Windows title bar; client area Minecraft-styled
- Header: green concrete; white title + dual shadow; Key Mode spruce combo with white shadow text
- Fields: left-column labels (14px); data boxes 15px
- Buttons: stone tile + bevel; white label + dark pixel shadow (no crafting grid)
- Font scale: base 14px; footer/copy 14px; status 13px

### UI readability pass (2026-07-07 afternoon)

Removed `crafting_grid.png`; enlarged fonts; restored field labels; Key Mode → spruce wood texture. Verified after clean rebuild.

### Layout sizing pass (2026-07-07)

| Change | Detail |
|--------|--------|
| Window default | 680×440 → **760×460** |
| Minimum size | 600×400 → **720×420** |
| Header grid | `* \| Auto` → **`Auto \| * \| Auto`** (title no longer truncates) |
| Label column | 110 px → **120 px** |
| Tooltips | Foreground `#FFFF88` → **#FFFFFF**, 14px |
| Footer button margin | 4 px → **2 px** horizontal |

**Why 680 ran 跑板:** title sat in `*` column and lost ~288 px after Key Mode (~360 px fixed); `"File Fingerprinting"` at 22px needs ~300–320 px. Footer `UniformGrid` at 680 px gave ~162 px/button — tight for EN `"Select a file"`.

See [ui-design.md](../implementation/ui-design.md) for full size differential table.

## Build and publish

```powershell
cd D:\Program_Coding\Q_Test\tpfilem-modern
dotnet test -c Release
.\tools\publish.ps1
# Dev run:
.\publish\app\FileFingerprinting.exe

# Installer:
.\tools\build-installer.ps1 -LegacyCoreSource "D:\...\TPFileM\TPFileM.exe"
```

(`build-installer.ps1` cleans and republishes staging automatically.)

### Clean rebuild (when UI does not update)

```powershell
Get-Process FileFingerprinting -ErrorAction SilentlyContinue | Stop-Process -Force
dotnet clean -c Release
Remove-Item -Recurse -Force publish\app, src\TpFileM.App\bin, src\TpFileM.App\obj -ErrorAction SilentlyContinue
.\tools\publish.ps1
```

Do **not** copy only `FileFingerprinting.exe`. End users on old `Program Files` installs must rerun **1.0.1** Setup.

## Verification record (2026-07-07)

| Check | Result |
|-------|--------|
| `dotnet test -c Release` | 9/9 pass |
| `dotnet build` TpFileM.App | 0 errors |
| `publish/app/FileFingerprinting.exe` | Starts, window stays open |
| `FileFingerprinting/1.0.1` in deps.json | Yes |
| `crafting_grid.png` absent from publish | Yes (removed) |
| `Assets/Textures/stone.png` in publish | Yes |
| `Assets/Fonts/Monocraft.ttf` in publish | Yes |
| Main exe size | ~427 KB (+ DLL folder) |
| Default window 760×460; Min 720×420 | Yes (`MainWindow.xaml`) |
| Header `Auto\|*\|Auto`; label col 120 px | Yes |
| ToolTip foreground #FFFFFF | Yes (`MinecraftTheme.xaml`) |

Manual UI sign-off (readability pass): stone buttons with white shadow text; spruce Key Mode readable; left-column field labels visible; no crafting grid on buttons.

Manual UI sign-off (layout pass): full EN title at 760 px; footer buttons single-line; white tooltips on dark concrete; resize to 720 min width — no title clip.

### Installer rebuild (2026-07-07 afternoon)

| Change | Detail |
|--------|--------|
| Clean build | `build-installer.ps1` removes stale `installer-staging`, `installer`, `app-multifile` before publish |
| Setup languages | English + **繁體中文** (`ChineseTraditional.isl` vendored in repo) |
| Setup branding | `logo.ico` as Setup icon; wizard small image from same logo |
| Product name | Localized Start Menu / shortcuts: File Fingerprinting / 文件指紋識別 |

### Installer verification (2026-07-07)

| Check | Result |
|-------|--------|
| `dotnet test -c Release` (via publish) | 9/9 pass |
| Staging files | 414 files; `PresentationFramework.dll` present |
| `runtime\LegacyCore.exe` in staging | Yes |
| `FileFingerprinting-Setup.exe` | ~68.7 MB; compiles with EN + zh-TW |
| Silent install smoke (`/VERYSILENT`) | Exit 0; full tree installed |
| Installed `FileFingerprinting.exe` | Starts, window stays open |

Manual sign-off: run Setup → confirm language picker (English / 繁體中文); wizard icon matches app logo.

## Files touched (reference)

- `src/TpFileM.App/TpFileM.App.csproj` — version, textures, font, `PublishSingleFile=false`
- `src/TpFileM.App/Themes/MinecraftTheme.xaml` — theme + button layer fix
- `src/TpFileM.App/MainWindow.xaml` — layout
- `src/TpFileM.App/Services/LocalizationService.cs` — resource suffix lookup
- `tools/publish.ps1`, `tools/build-installer.ps1`, `tools/installer/FileFingerprinting.iss`
- `tools/installer/languages/ChineseTraditional.isl`, `tools/installer/prepare-wizard-assets.ps1`
- `tools/installer/FileFingerprinting.iss` — `AppVersion=1.0.1`, zh-TW wizard, logo, full tree copy
