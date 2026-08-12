# Build app

Developer workflow. End-user install: [build-installer.md](build-installer.md) and [user install](../user/install.md).

```powershell
cd D:\Program_Coding\Q_Test\tpfilem-modern
dotnet build
dotnet test
```

## Release publish (multi-file)

WPF GUI is published as a **folder** (`PublishSingleFile=false`) — run `FileFingerprinting.exe` from `publish/app/`, do not copy the exe alone.

```powershell
.\tools\publish.ps1
```

Output:

| Artifact | Role |
|----------|------|
| `publish/app/FileFingerprinting.exe` | WPF GUI entry (+ DLLs beside it) |
| `publish/app/TpFileM.Mcp.exe` | MCP server |
| `publish/app/TpFileM.LegacySha.Cli.exe` | win-x86 legacy SHA helper |

Dev runtime: `TPFILEM_LEGACY_EXE` or `../TPFileM/TPFileM.exe` — see [legacy-sha-dependency](../dev/legacy-sha-dependency.md).

## End-user installer

```powershell
.\tools\publish.ps1 -ForInstaller
.\tools\build-installer.ps1 -LegacyCoreSource "D:\...\TPFileM\TPFileM.exe"
```

## Manual publish

Same as `publish.ps1` — **multi-file only** for the WPF GUI:

```powershell
dotnet publish src/TpFileM.App `
  -c Release `
  -r win-x64 `
  --self-contained `
  -p:PublishSingleFile=false `
  -o publish/app
```

Produces `FileFingerprinting.exe` plus runtime DLLs in `publish/app/`. See [bug reports](../dev/bug-reports.md) (FF-002) for why single-file publish is disabled.
