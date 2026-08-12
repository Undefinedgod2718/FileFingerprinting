# Ghidra decompile vs C# Core

**Archived (2026-07-07)** — superseded by [SHA GUI investigation](../sha-gui-investigation.md) (SHA) and [CRC32 analysis](../crc32-analysis.md) (CRC GUI path). Historical Ghidra MCP session notes.

Verified via Ghidra MCP (`connect_instance("SC")`, `create_function`, `decompile_function`) on 2026-07-06.

## CRC compute — `crc_compute_file` @ `0x004019C0`

### Legacy pseudocode (essential)

```c
uint crc = 0xFFFFFFFF;
do {
    ReadFile(handle, buf, 0x2000, &n, NULL);
    if (n == 0) break;
    for each byte b in buf:
        crc = (crc >> 8) ^ table[(crc & 0xFF) ^ b];   // table at this+0x7C
} while (ReadFile succeeded);
return ~crc;
```

### C# mapping — [`Crc32.cs`](../../../src/TpFileM.Core/Crc32.cs)

| Legacy | C# |
|--------|-----|
| `crc = 0xFFFFFFFF` | `uint crc = 0xFFFFFFFF` |
| `(crc & 0xFF) ^ byte` | `(crc ^ b) & 0xFF` |
| `crc >> 8 ^ table[idx]` | `(crc >> 8) ^ Table[index]` |
| `return ~crc` | `return ~crc` |
| `ReadFile` 0x2000 chunks | `KeyGenerator` reads in `0x2000` chunks (equivalent over full file) |

**Note:** This Ghidra path uses a custom CRC table @ `0x004019C0`. The **GUI** uses zlib CRC — see [CRC32 analysis](../crc32-analysis.md).

## CRC table build — `crc_build_table` @ `0x00401790`

Legacy uses helper `FUN_004017f0(value, n)` = **reverse lower `n` bits** of `value`.

```c
for (i = 0; i < 256; i++) {
    v = bitreverse8(i) << 24;
    repeat 8: MSB-first shift with poly 0x04C11DB7
    table[i] = bitreverse32(v);
}
```

C# `BuildTable()` uses the simplified form without explicit bit-reversal:

```csharp
uint crc = (uint)(i << 24);
// same 8 MSB-first steps with 0x04C11DB7
table[i] = crc;
```

Empirical check (`tools/crc_check.py` extended): **both tables produce identical CRC keys** for all verified vectors (`empty`, `123456789`, `test`, `0..15`). The simplified table is an equivalent parameterization — no C# change required.

## SHA file path — `sha_compute_file` @ `0x00402060`

```c
sha1_init(ctx);
do {
    ReadFile(handle, buf, 0x2000, &n, NULL);
    if (n == 0) break;
    sha1_update(ctx, buf, n);
} while (...);
sha1_final(ctx);
```

Chunked read does not change digest. Modern [`Hasher.cs`](../../../src/TpFileM.Core/Hasher.cs) delegates SHA to [`LegacySha1`](../../../src/TpFileM.Core/LegacySha1.cs) → CLI.

**GUI mismatch (resolved 2026-07-07):** Initial disasm suggested RFC SHA-1; GUI golden required native helper path — see [SHA GUI investigation](../sha-gui-investigation.md).

## Generate Key handler — `generate_key_handler` @ `0x004021F0`

```
FUN_00401c30 (CRC) → CreateFile → sha_compute_file → format_sha_key
```

`format_sha_key` @ `0x004021A0` formats SHA context dwords `[0..4]` with `%08X %08X %08X %08X %08X` @ `0x41D1BC`.

## MCP functions created in Ghidra

| Address | Name | Purpose |
|---------|------|---------|
| `0x00401790` | `crc_build_table` | 256-entry CRC table |
| `0x004019C0` | `crc_compute_file` | CRC over file |
| `0x00401CE0` | `sha1_compress` | SHA-1 block compression |
| `0x00402060` | `sha_compute_file` | SHA-1 over file |

## Conclusion (historical)

At time of writing, authors believed modern `TpFileM.Core` matched legacy **observable behavior** via standard SHA-1. Post-golden investigation, SHA requires the native CLI path; CRC uses zlib in-process.
