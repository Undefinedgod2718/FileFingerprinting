# Developer documentation

> **Before changing hashing, installer runtime, or Key Mode** — read [Legacy SHA dependency](legacy-sha-dependency.md).

## Required reading

- [Legacy SHA dependency](legacy-sha-dependency.md) — CRC vs SHA independence; common mistakes
- [Documentation conventions](../conventions.md)

## Project phases

| Phase | Topic | Doc |
|-------|-------|-----|
| 1 | Legacy CRC + SHA parity | [test vectors](../testing/test-vectors.md), [sha-gui-investigation](../reverse-engineering/sha-gui-investigation.md) |
| 2 | Modern PKI | [modern-key-spec](../security/modern-key-spec.md) |
| 3 | HashTool + MSIX Store | (planned) |

## Build and publish

- [Prerequisites](../build/prerequisites.md)
- [Build app](../build/build-app.md)
- [Build MCP](../build/build-mcp.md)
- [Build installer](../build/build-installer.md)
- [Bug reports](bug-reports.md) — version-specific defects and fixes
- [Release 1.0.1](release-1.0.1.md) — changelog, UI theme, verification record

## Testing

- [Verification strategy](../testing/verification-strategy.md)
- [Test vectors](../testing/test-vectors.md)
- [Manual GUI parity](../testing/manual-gui-parity.md)

## Implementation

- [Architecture](../implementation/architecture.md)
- [Core algorithms](../implementation/core-algorithms.md)
- [UI design](../implementation/ui-design.md)

## Reverse engineering

- [Wiki RE index](../README.md#reverse-engineering) — see main wiki index under Developer sections

## MCP

- [TpFileM MCP server](../mcp/tpfilem-mcp-server.md)
- [Ghidra MCP](../mcp/ghidra-mcp.md)

## User-facing docs (do not merge into installer)

- [User install](../user/install.md)
- [User overview](../user/overview.md)
