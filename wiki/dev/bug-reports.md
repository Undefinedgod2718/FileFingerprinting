# Bug reports

**Status:** Active log — File Fingerprinting release defects and fixes.

Product version in installer: **1.0.1** (`tools/installer/FileFingerprinting.iss`).

## Version matrix

| Label | App version | Approx. date | How to recognize | Startup | Installer |
|-------|-------------|--------------|------------------|---------|-----------|
| **Pre-fix** | 1.0.0 | ≤ 2026-07-06 | `FileFingerprinting.exe` ≈ **140 MB** (single-file); or dev build with `strings.en.json` / `strings.zh-TW.json` | ❌ Crashes on launch | ❌ May ship only 3 files (missing .NET runtime DLLs) |
| **Post-fix (interim)** | 1.0.0 | 2026-07-07 | `publish/app/` multi-file; strings `strings-en.json` / `strings-zh-TW.json`; flat-color UI | ✅ Verified | ✅ Full staging tree |
| **Current release** | **1.0.1** | 2026-07-07 (verified) | Multi-file `publish/app/`; Minecraft UI; white button labels; `AppVersion=1.0.1` | ✅ 9/9 tests + GUI smoke | ✅ Full staging tree |

See [release-1.0.1.md](release-1.0.1.md) for full changelog and verification record.

---

## FF-001 — Startup crash loading UI strings

| Field | Value |
|-------|-------|
| **Severity** | Critical (app unusable) |
| **Affected versions** | 1.0.0 pre-fix |
| **Fixed in** | **1.0.1** (also fixed in interim 1.0.0 post-fix build, 2026-07-07) |
| **Component** | `TpFileM.App` / `LocalizationService` |

### Symptom

Application exits immediately on launch. No window.

### Error (typical)

```
System.Text.Json.JsonException: '0xEF' is an invalid start of a value.
   at TpFileM.App.Services.LocalizationService.LoadStrings(...)
```

Exit code may appear as `-532462766` (`0xE0434352` — unhandled .NET exception).

### Root cause

1. Embedded resource files were named `strings.en.json` and `strings.zh-TW.json`.
2. MSBuild treated `*.en.json` / culture suffixes as **satellite assemblies**, not plain embedded resources.
3. `LocalizationService` looked up hard-coded manifest names that did not match the built assembly.
4. Fallback logic read `*.g.resources` (binary WPF resource bundle) as UTF-8 JSON → BOM `0xEF` parse failure.

### Fix

- Rename assets to `Assets/strings-en.json` and `Assets/strings-zh-TW.json` (no `.en.` culture segment).
- Keep them as `<EmbeddedResource>` in `TpFileM.App.csproj`.
- Resolve resources by suffix in `LocalizationService.OpenResourceStream` (see `Assets.strings-en.json` / `Assets.strings-zh-TW.json`).

### Verification

```powershell
dotnet test -c Release
# Launch from bin or publish folder — window opens, language toggle works
```

---

## FF-002 — Startup crash with single-file publish

| Field | Value |
|-------|-------|
| **Severity** | Critical (published app unusable) |
| **Affected versions** | 1.0.0 pre-fix (`PublishSingleFile=true` for GUI) |
| **Fixed in** | **1.0.1** (also fixed in interim 1.0.0 post-fix build, 2026-07-07) |
| **Component** | Publish profile / `TpFileM.App.csproj` |

### Symptom

`publish/app/FileFingerprinting.exe` (~140 MB single-file) exits immediately. `dotnet run` or multi-file `bin/Release` build may still work.

### Error (typical)

Unhandled exception at startup; exit code `-532462766` (`0xE0434352`). No UI.

### Root cause

WPF + self-contained **single-file** publish does not reliably load embedded resources and companion files at startup for this app. The bundled extraction path conflicts with how `LocalizationService` and WPF load `EmbeddedResource` / `Assets/logo.ico`.

### Fix

- Set `PublishSingleFile=false` in `src/TpFileM.App/TpFileM.App.csproj`.
- `tools/publish.ps1` passes `-p:PublishSingleFile=false` for GUI publish (installer staging and `publish/app/`).
- Ship the **entire** `publish/app/` directory (or use the installer). **Do not copy only `FileFingerprinting.exe`.**

`TpFileM.Mcp.exe` and `TpFileM.LegacySha.Cli.exe` remain single-file where appropriate.

### Verification

```powershell
.\tools\publish.ps1
$p = Start-Process "publish\app\FileFingerprinting.exe" -PassThru
# Window stays open; exe size ~427 KB with hundreds of DLLs beside it
```

---

## FF-003 — Installer missing runtime files

| Field | Value |
|-------|-------|
| **Severity** | High (installed app won't start) |
| **Affected versions** | 1.0.0 pre-fix installer (`FileFingerprinting.iss` copied 3 files only) |
| **Fixed in** | **1.0.1** (also fixed in interim 1.0.0 post-fix build, 2026-07-07) |
| **Component** | `tools/installer/FileFingerprinting.iss` |

### Symptom

Setup completes, but installed **File Fingerprinting** won't start (same crash as FF-002) because `Program Files\File Fingerprinting\` lacks .NET / WPF DLLs.

### Root cause

Inno Setup `[Files]` section listed only:

- `FileFingerprinting.exe`
- `TpFileM.LegacySha.Cli.exe`
- `runtime\LegacyCore.exe`

Multi-file GUI publish requires the full publish output tree.

### Fix

```iss
Source: "{#StagingDir}\*"; DestDir: "{app}";
  Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "*.pdb"
```

Rebuild: `publish.ps1 -ForInstaller` → `build-installer.ps1`.

### Verification

Install `publish/installer/FileFingerprinting-Setup.exe`; confirm install folder contains `PresentationFramework.dll`, `FileFingerprinting.dll`, etc.

---

## FF-004 — Button labels unreadable (crafting grid experiment)

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Affected versions** | 1.0.1 UI builds 2026-07-07 (crafting-grid buttons) |
| **Fixed in** | **1.0.1** readability pass (2026-07-07, verified) |
| **Component** | `Themes/MinecraftTheme.xaml` |

### Symptom

Button labels dark or grid lines visually cut through text. Poor contrast vs reference UI.

### Root cause

`crafting_grid.png` tiled on buttons; `ContentTemplate` / layering still insufficient for readable labels.

### Fix (final)

- **Remove** `crafting_grid.png` from UI entirely
- Buttons: `McTileStone` + beveled border + white `#FFFFFF` text with 1px `#1A1A1A` shadow (`TemplateBinding Content`)
- See [ui-design.md](../implementation/ui-design.md) current button template

---

## FF-006 — Missing field labels

| Field | Value |
|-------|-------|
| **Severity** | Medium (UX — users unclear what boxes mean) |
| **Affected versions** | 1.0.1 initial Minecraft layout (labels hidden, `AutomationProperties` only) |
| **Fixed in** | **1.0.1** readability pass (2026-07-07) |
| **Component** | `MainWindow.xaml` |

### Symptom

Three read-only fields have no visible titles; operators cannot tell file name vs CRC vs SHA.

### Fix

Restore left-column `FileNameLabel`, `CrcKeyLabel`, `ShaKeyLabel` (110px) with `McFieldLabel` style; keep `AutomationProperties` for screen readers.

---

## FF-007 — Key Mode combo low contrast / wrong texture

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Affected versions** | 1.0.1 before readability pass (dark concrete combo, 12px text) |
| **Fixed in** | **1.0.1** readability pass (2026-07-07) |
| **Component** | `McKeyModeCombo` |

### Symptom

Key Mode dropdown hard to read; does not match spruce-wood reference on green header.

### Fix

- Background: `McTileSpruce`
- Border: `#3A2E1E`
- Text: 14px white + pixel shadow
- Label: `McHeaderKeyModeLabel` with matching shadow

---

## FF-008 — Layout squeeze at 680×440; tooltip text unreadable

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Affected versions** | 1.0.1 before layout pass (680×440 default, `MinWidth=600`) |
| **Fixed in** | **1.0.1** layout pass (2026-07-07) |
| **Component** | `MainWindow.xaml`, `MinecraftTheme.xaml` ToolTip style |

### Symptom

- Header title clipped (`"File Fingerprinti"` instead of full title)
- Footer buttons cramped; EN labels tight; tooltips overlap adjacent buttons
- Tooltip foreground yellow (`#FFFF88`) on dark concrete — hard to read

### Root cause

- Header grid `* | Auto`: title in star column lost width to fixed Key Mode combo (~360 px)
- `UniformGrid` at 680 px → ~162 px per footer button
- ToolTip style used yellow foreground

### Fix

- Window **760×460**, `MinWidth=720`, `MinHeight=420`
- Header grid **`Auto | * | Auto`**
- Label column 110 → **120 px**
- ToolTip `Foreground="#FFFFFF"`, `FontSize=14`
- Footer button horizontal margin 4 → **2 px**

### Verification

Full EN title at 760 px; footer single-line; white tooltips; resize to 720 min — no title clip. See [ui-design.md](../implementation/ui-design.md).

---

## FF-005 — Stale publish folder shows old UI

| Field | Value |
|-------|-------|
| **Severity** | Low (operator confusion; not a code defect in current tree) |
| **Affected versions** | Any — when old `publish/app` or `Program Files` copy is run |
| **Fixed in** | **1.0.1** process documented |
| **Component** | Publish / install workflow |

### Symptom

Developer or tester runs `FileFingerprinting.exe` but UI looks unchanged (flat colors, dark button text, or pre-1.0.1 layout).

### Root cause

- Incremental publish left old `FileFingerprinting.dll` / BAML cached
- User launched exe from wrong path (old installer dir, desktop shortcut to 1.0.0, or copied lone exe)
- Running process locked DLL during rebuild

### Fix

1. Stop all `FileFingerprinting.exe` processes
2. `dotnet clean -c Release`; delete `publish/app`, `src/TpFileM.App/bin`, `src/TpFileM.App/obj`
3. `.\tools\publish.ps1` — launch from `publish\app\FileFingerprinting.exe`
4. End users: reinstall **FileFingerprinting-Setup.exe** at **1.0.1**

### Verification

Compare `FileFingerprinting.dll` timestamp with `MinecraftTheme.xaml` source; deps.json shows `FileFingerprinting/1.0.1`.

---

## Reporting new issues

When logging a defect:

1. Add a row to this page with ID `FF-00N`.
2. Set **Affected versions** / **Fixed in** using `AppVersion` from the installer and build date.
3. Link verification steps (test command or manual checklist).
4. Update [user install troubleshooting](../user/install.md) if end users can hit the issue.
5. Add the page to [wiki index](../README.md) if creating a new file.
