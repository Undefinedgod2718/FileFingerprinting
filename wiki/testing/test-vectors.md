# Test vectors

Golden CRC values from **Delta TPFileM.exe GUI** (2026-07-06) and zlib formula. SHA aligned via Unicorn emulation (2026-07-07).

## CRC (GUI / zlib)

| Input | CRC Key | GUI verified |
|-------|---------|--------------|
| *(empty)* | `00000000` | zlib only |
| ASCII `123456789` | `CBF43926` | yes (`digits.bin`) |
| ASCII `test` | `D87F7E0C` | zlib only |
| bytes `0x00..0x0F` | `CECEE288` | zlib only |
| `0x100216 PLC offline trouble shooting.docx` | `A25E39C9` | yes |

Machine-readable: [`tools/fixtures/legacy-golden.json`](../../tools/fixtures/legacy-golden.json)

## SHA Key (GUI)

| Fixture | SHA Key (legacy GUI) | Status |
|---------|----------------------|--------|
| `empty.bin` | `241DEE2C 252BF5C0 6A31228F 06EA7320 0511F520` | Locked |
| `digits.bin` | `67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD` | Locked (Unicorn + GUI) |
| `test.bin` | `0E6AD8B3 B29925F7 93802DA5 09E31588 4DB93485` | Locked |
| `seq16.bin` | `8CC3A456 BCED0FFD 87F17B4A 2F2F4A0D BB8A968F` | Locked |
| docx | `BB741E73 A3136085 49B3225A C5F9B80B E0287945` | Locked (GUI; optional path) |

Modern `Hasher` uses `TpFileM.LegacySha.Cli.exe` (win-x86). See [`sha-gui-investigation.md`](../reverse-engineering/sha-gui-investigation.md).

## SHA-1 RFC reference (`abc`)

Full digest: `A9993E364706816ABA3E25717850C26C9CD0D89D`

Formatted (big-endian words):

```
A9993E36 4706816A BA3E2571 7850C26C 9CD0D89D
```

## Legacy GUI capture log

| Fixture | CRC (legacy) | SHA (legacy) | Date | Notes |
|---------|--------------|--------------|------|-------|
| `digits.bin` | `CBF43926` | `67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD` | 2026-07-06 | CRC locked; SHA golden recorded |
| docx | `A25E39C9` | `BB741E73…` | 2026-07-06 | CRC locked when path exists |
