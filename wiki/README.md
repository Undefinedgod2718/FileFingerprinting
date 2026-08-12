# Wiki index

English documentation for the File Fingerprinting project (`tpfilem-modern` repo).

## User documentation

For operators installing and using the app:

- [Install](user/install.md)
- [Overview](user/overview.md)

## Developer documentation

**Start here:** [dev/README.md](dev/README.md) — includes mandatory [Legacy SHA dependency](dev/legacy-sha-dependency.md).

### Projects & Publish Output

| Project / Artifact | Role / Purpose |
|--------------------|----------------|
| `TpFileM.App` | WPF GUI → publishes as `FileFingerprinting.exe` |
| `TpFileM.Core` | CRC (zlib) + legacy SHA orchestration |
| `TpFileM.LegacySha.Cli` | win-x86 native SHA helper (publishes to `publish/app/TpFileM.LegacySha.Cli.exe`) |
| `TpFileM.Mcp` | MCP server (stdio) (publishes to `publish/app/TpFileM.Mcp.exe`) |
| `TpFileM.Core.Tests` | xUnit regression tests |

*Publish command:* `.\tools\publish.ps1`

Maintainers: [Documentation conventions](conventions.md).

### Reverse engineering

- [Ghidra setup](reverse-engineering/ghidra-setup.md)
- [Binary overview](reverse-engineering/binary-overview.md)
- [CRC32 analysis](reverse-engineering/crc32-analysis.md)
- [SHA GUI investigation](reverse-engineering/sha-gui-investigation.md) *(resolved — SHA runtime spec)*
- [Filename validation](reverse-engineering/filename-validation.md)
- [Function map](reverse-engineering/function-map.md)
- **Archive**
  - [SHA-1 analysis (stub)](reverse-engineering/sha1-analysis.md) → [archive](reverse-engineering/archive/sha1-analysis.md)
  - [Ghidra decompile CRC/SHA (stub)](reverse-engineering/ghidra-decompile-crc.md) → [archive](reverse-engineering/archive/ghidra-decompile-crc.md)

### Implementation

- [Overview (technical)](overview.md)
- [Architecture](implementation/architecture.md)
- [Core algorithms](implementation/core-algorithms.md)
- [UI design](implementation/ui-design.md)

### Build

- [Prerequisites](build/prerequisites.md)
- [Build app](build/build-app.md)
- [Build installer](build/build-installer.md)
- [Build MCP](build/build-mcp.md)
- [Run legacy](build/run-legacy.md)

### Quality

- [Release 1.0.1](dev/release-1.0.1.md) — changelog and verification
- [Bug reports](dev/bug-reports.md) — known defects by version (developer)

### Testing

- [Verification strategy](testing/verification-strategy.md)
- [Parallel testing](testing/parallel-testing.md)
- [Test vectors](testing/test-vectors.md)
- [Manual GUI parity](testing/manual-gui-parity.md)

### Security

- [Modern key spec (Phase 2)](security/modern-key-spec.md)

### MCP

- [Ghidra MCP](mcp/ghidra-mcp.md)
- [TpFileM MCP server](mcp/tpfilem-mcp-server.md)
