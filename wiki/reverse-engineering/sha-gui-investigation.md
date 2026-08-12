# SHA GUI investigation

**Status:** Resolved (2026-07-07) — GUI golden reproduced. Runtime uses **`TpFileM.LegacySha.Cli`** (win-x86 PE mapper + native SHA routines from `TPFileM.exe`). No Python at publish time.

## GUI golden

| Fixture | Legacy SHA Key |
|---------|----------------|
| `digits.bin` | `67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD` |
| `test.bin` | `0E6AD8B3 B29925F7 93802DA5 09E31588 4DB93485` |
| `seq16.bin` | `8CC3A456 BCED0FFD 87F17B4A 2F2F4A0D BB8A968F` |
| `empty.bin` | `241DEE2C 252BF5C0 6A31228F 06EA7320 0511F520` |
| docx | `BB741E73 A3136085 49B3225A C5F9B80B E0287945` |

## Algorithm (non-RFC SHA-1 variant)

Custom W expansion + LE length at `ctx+0x54/0x58`; rounds read from `W[2]`. Historical RFC SHA-1 hypothesis: [archive/sha1-analysis.md](archive/sha1-analysis.md).

## Runtime architecture

```
TpFileM.Core.LegacySha1  →  spawn  TpFileM.LegacySha.Cli.exe (win-x86)
                              →  map TPFileM.exe @ relocated base
                              →  call 0x1EF0 init / 0x1F30 update / 0x1FD0 final
```

`sha_final` requires **ECX** register — handled by `X86Thunk` in the CLI.

## Dev oracles

| Tool | Role |
|------|------|
| [`tools/unicorn_sha.py`](../../tools/unicorn_sha.py) | Unicorn emulation oracle |
| [`tools/sha_parity_check.py`](../../tools/sha_parity_check.py) | CLI vs unicorn / GUI golden |

## Verification

```powershell
dotnet test -c Release
python tools\sha_parity_check.py
```

Manual GUI: [`wiki/testing/manual-gui-parity.md`](../testing/manual-gui-parity.md)
