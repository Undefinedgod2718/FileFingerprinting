# CRC32 analysis

## GUI behavior (authoritative)

**Delta TPFileM.exe** displays **PKZIP / zlib CRC-32** on the **CRC Key** field — same as Python `binascii.crc32` / .NET `System.IO.Hashing.Crc32`.

| File | GUI CRC | zlib |
|------|---------|------|
| `digits.bin` (`123456789`) | `CBF43926` | `CBF43926` |
| `0x100216…docx` | `A25E39C9` | `A25E39C9` |

Modern implementation: [`src/TpFileM.Core/Crc32.cs`](../../src/TpFileM.Core/Crc32.cs) uses `System.IO.Hashing.Crc32`.

## Ghidra RE finding (not GUI path)

Static analysis located a **different** CRC variant at `0x004019C0`:

| Item | Address / value |
|------|-----------------|
| Polynomial constant | `.text+0x17C0` → `0x04C11DB7` |
| Table builder | `0x00401790` |
| Init / final | `0xFFFFFFFF` / `NOT EAX` @ `0x401AF6` |
| Read chunk | `0x2000` bytes |

This produces e.g. `123456789` → `7EAD5C77`, **not** the GUI value `CBF43926`. Treat as **dead or alternate code path** until proven otherwise.

## zlib spec (what we ship)

```
crc = 0xFFFFFFFF
for each byte b:
    crc = table[(crc XOR b) AND 0xFF] XOR (crc >> 8)   // reflected
return crc XOR 0xFFFFFFFF
```

Polynomial: `0xEDB88320` (reflected form of IEEE 802.3)

## Verified vectors (GUI + tests)

| Input | CRC Key |
|-------|---------|
| *(empty)* | `00000000` |
| `123456789` | `CBF43926` |
| `test` | `D87F7E0C` |
| bytes `0..15` | `CECEE288` |

Golden file: [`tools/fixtures/legacy-golden.json`](../../tools/fixtures/legacy-golden.json)

## RE-only vectors (0x04C11DB7 path)

| Input | CRC Key |
|-------|---------|
| `123456789` | `7EAD5C77` |
| `test` | `49541D5A` |
| bytes `0..15` | `C0A0FEF9` |

See [`tools/crc_check.py`](../../tools/crc_check.py) (`re_custom` vs `gui_zlib`). Ghidra notes on the `0x04C11DB7` path: [archive/ghidra-decompile-crc.md](archive/ghidra-decompile-crc.md).
