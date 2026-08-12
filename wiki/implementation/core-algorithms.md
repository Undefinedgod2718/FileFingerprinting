# Core algorithms (modern rewrite)

## Principle

Reverse engineering produces a **behavior spec**. The C# code is written from scratch to match legacy **outputs**, not to mirror 2006 control flow.

## Components

| Type | Responsibility |
|------|----------------|
| `Crc32` | Legacy polynomial + table + reflected update |
| `Hasher` | Legacy SHA via `LegacySha1` → `TpFileM.LegacySha.Cli.exe` + LE `%08X` formatting |
| `FilenameValidator` | Path checks + legacy error strings |
| `KeyGenerator` | Read file → CRC + SHA → `KeyResult` |

## Chunked reads

Legacy reads **`0x2000`** bytes per `ReadFile` call. Modern `KeyGenerator` reads the full file in the same chunk size before hashing (equivalent for in-memory hashing).

## Forbidden

- Pasting Ghidra decompiler output into C#
- Custom SHA-1 compression
