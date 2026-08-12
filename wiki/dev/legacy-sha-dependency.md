# Legacy SHA dependency (developer)

**Status:** Locked as of Phase 1 (2026-07-07).

End users install **File Fingerprinting** only. Developers must understand: **hiding the dependency is not removing it.**

## Summary

| Output | Independent of legacy PE? | Implementation |
|--------|---------------------------|----------------|
| **CRC Key** | **Yes** | [`Crc32.cs`](../../src/TpFileM.Core/Crc32.cs) — `System.IO.Hashing` |
| **Legacy SHA Key** | **No** | [`LegacySha1.cs`](../../src/TpFileM.Core/LegacySha1.cs) → `TpFileM.LegacySha.Cli.exe` → maps [`runtime/LegacyCore.exe`](../user/install.md) (original 32-bit code) |

Pure C# / RFC SHA-1 **does not** match GUI golden. See [SHA GUI investigation](../reverse-engineering/sha-gui-investigation.md).

## Runtime chain

```
FileFingerprinting.exe
  → KeyGenerator / Hasher
  → CRC: in-process
  → SHA: LegacySha1.ComputeFile
       → spawn TpFileM.LegacySha.Cli.exe (win-x86)
       → load runtime\LegacyCore.exe
       → native SHA @ 0x1EF0 / 0x1F30 / 0x1FD0
```

Installer layout (user machine):

```
%ProgramFiles%\File Fingerprinting\
  FileFingerprinting.exe
  TpFileM.LegacySha.Cli.exe
  runtime\LegacyCore.exe
```

`LegacyCore.exe` is copied at **build time** from the authorized legacy binary (`build-installer.ps1 -LegacyCoreSource`). It is **not** committed to git.

## Developer overrides

| Mechanism | Audience |
|-----------|----------|
| `runtime\LegacyCore.exe` beside app | Installed / staged builds |
| `TPFILEM_LEGACY_EXE` | Local dev only — see [build-installer.md](../build/build-installer.md) |
| Walk up to `../TPFileM/TPFileM.exe` | Repo dev layout |

Hard-coded `D:\...` paths were removed from [`Program.cs`](../../src/TpFileM.LegacySha.Cli/Program.cs).

## Common mistakes (do not do this)

1. **Replace Legacy SHA with `SHA1.HashData`** — breaks [`legacy-golden.json`](../../tools/fixtures/legacy-golden.json).
2. **Assume “no TPFileM in user docs” means SHA is standalone** — `LegacyCore.exe` is still required.
3. **Use one enum value for “SHA-1” and “Legacy SHA Key”** — Phase 3 standard hashes must stay separate.
4. **Ship only `FileFingerprinting.exe`** — SHA path fails without Cli + `runtime\`.
5. **Treat Phase 2 PKI as replacing Legacy SHA** — PKI is for new devices; legacy fingerprints still need this chain.

## Verification

```powershell
dotnet test -c Release
```

Golden: [`tools/fixtures/legacy-golden.json`](../../tools/fixtures/legacy-golden.json).

## References

- [Core algorithms](../implementation/core-algorithms.md)
- [LegacySha.Cli Program.cs](../../src/TpFileM.LegacySha.Cli/Program.cs)
