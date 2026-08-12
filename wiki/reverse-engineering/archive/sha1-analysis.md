# SHA-1 analysis

**Archived (2026-07-07)** — superseded by [SHA GUI investigation](../sha-gui-investigation.md). Initial disasm assumed RFC SHA-1 matched GUI output; golden tests proved a non-RFC native path.

## Summary

Legacy binary contains SHA-1-like routines @ `0x00401CE0` with recognizable round constants (`0x5A827999`, `0x6ED9EBA1`, …). Early analysis treated this as standard **SHA-1** (RFC 3174). A naive RFC port **does not** match GUI output.

Modern runtime (post-archive): **`LegacySha1`** → spawn **`TpFileM.LegacySha.Cli.exe`** (native routines from mapped `TPFileM.exe`).

## Output format

Digest is formatted as **five big-endian 32-bit words**, uppercase hex, space-separated:

```
%08X %08X %08X %08X %08X
```

String RVA: `0x41D1BC`

Example (`abc`, RFC reference only — **not** legacy GUI output):

```
A9993E36 4706816A BA3E2571 7850C26C 9CD0D89D
```

## File input

Same full file content as CRC, read in chunks during `0x00402060` (wrapper) calling `0x00401CE0`.

## Modern implementation (at time of archival)

[`Hasher.cs`](../../../src/TpFileM.Core/Hasher.cs) formats digest; computation in [`LegacySha1.cs`](../../../src/TpFileM.Core/LegacySha1.cs) via `TpFileM.LegacySha.Cli.exe`.
