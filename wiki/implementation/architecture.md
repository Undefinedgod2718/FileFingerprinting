# Architecture

```
TpFileM.sln
├── src/TpFileM.Core/           # CRC (zlib) + legacy SHA orchestration
├── src/TpFileM.LegacySha.Cli/  # win-x86 native SHA helper
├── src/TpFileM.App/            # WPF host
├── src/TpFileM.Mcp/            # stdio MCP tools
└── tests/TpFileM.Core.Tests/
```

## Dependency flow

```
TpFileM.App  ──┐
TpFileM.Mcp  ──┼──> TpFileM.Core ──spawn──> TpFileM.LegacySha.Cli.exe
Tests        ──┘                              (maps TPFileM.exe @ runtime)
```

## Design rules

1. **Spec-driven RE** — wiki documents behavior, not decompiled C++ ([conventions](../conventions.md))
2. **Clean C# core** — zlib CRC via `System.IO.Hashing`; legacy SHA via CLI subprocess (non-RFC variant)
3. **No registry / INI** from legacy app
4. **Phase 1** — Legacy key mode only; Modern PKI deferred ([modern-key-spec](../security/modern-key-spec.md))
