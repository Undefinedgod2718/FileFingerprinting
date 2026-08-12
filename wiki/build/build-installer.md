# Build installer (developer)

Produces **`FileFingerprinting-Setup.exe`** for end users. See [user install](../user/install.md) for what operators receive.

**Prerequisites**

- [.NET 10 SDK](prerequisites.md)
- [Inno Setup 6](https://jrsoftware.org/isinfo.php) (`ISCC.exe` on PATH or default install path)
- Path to authorized legacy binary for SHA mapping (not in git)

## Steps

`build-installer.ps1` **always** cleans stale `installer-staging`, `installer`, and `app-multifile`, runs a fresh `publish.ps1 -ForInstaller`, generates wizard assets, copies `LegacyCore.exe`, then compiles with ISCC.

```powershell
cd D:\Program_Coding\Q_Test\tpfilem-modern

.\tools\build-installer.ps1 -LegacyCoreSource "D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe"
```

(`publish.ps1 -ForInstaller` is invoked automatically; `dotnet test` runs inside `publish.ps1`.)

**Output:** `publish/installer/FileFingerprinting-Setup.exe`

**Staging (intermediate):** `publish/installer-staging/` — full multi-file publish tree (GUI + helpers), not a lone exe.

| Artifact | Role |
|----------|------|
| `FileFingerprinting.exe` | WPF GUI entry (~427 KB; requires sibling DLLs) |
| `FileFingerprinting.dll`, `TpFileM.Core.dll`, … | .NET / WPF runtime beside exe |
| `Assets/logo.ico` | Window icon (content) |
| `TpFileM.LegacySha.Cli.exe` | win-x86 SHA helper (single-file) |
| `runtime/LegacyCore.exe` | Copied from `-LegacyCoreSource` at build time |

## Installer wizard (1.0.1)

| Item | Source |
|------|--------|
| Languages | English + **繁體中文** (`tools/installer/languages/ChineseTraditional.isl`) — language picker at Setup start |
| Product name (localized) | `File Fingerprinting` / `文件指紋識別` via `[CustomMessages]` |
| Setup / Uninstall icon | `src/TpFileM.App/Assets/logo.ico` (`SetupIconFile`) |
| Wizard small image | `tools/installer/assets/wizard_small.bmp` (55×58, generated from `logo.ico` by `prepare-wizard-assets.ps1`) |

End users receive **only** `FileFingerprinting-Setup.exe`; do not ship `publish/app/` or `installer-staging/`.

Inno Setup copies the entire staging directory (`recursesubdirs`). Pre-fix installers that listed only three files failed at runtime — see [FF-003](../dev/bug-reports.md).

## Dev override

Set `TPFILEM_LEGACY_EXE` to point at a legacy binary when running from `dotnet run` without `runtime\LegacyCore.exe`. Documented here only — not in [user install](../user/install.md).

## Related

- [Legacy SHA dependency](../dev/legacy-sha-dependency.md)
- [Build app](build-app.md) — developer publish without installer
