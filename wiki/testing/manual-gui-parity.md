# Manual GUI parity checklist

Compare **legacy** `TPFileM.exe` vs **modern** `FileFingerprinting.exe` on the same file bytes.

## Prerequisites

```powershell
cd D:\Program_Coding\Q_Test\tpfilem-modern
.\tools\publish.ps1
& "D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe"
& ".\publish\app\FileFingerprinting.exe"
```

## Fixtures

| Fixture | CRC (expected) | SHA (expected) |
|---------|----------------|----------------|
| `tools/fixtures/digits.bin` | `CBF43926` | `67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD` |
| `tools/fixtures/test.bin` | `D87F7E0C` | `0E6AD8B3 B29925F7 93802DA5 09E31588 4DB93485` |
| docx (local path in `legacy-golden.json`) | `A25E39C9` | `BB741E73 A3136085 49B3225A C5F9B80B E0287945` |

Golden source: [`tools/fixtures/legacy-golden.json`](../../tools/fixtures/legacy-golden.json)

## Steps (per fixture)

1. Open the file in **legacy** TPFileM → **Generate Key**
2. Screenshot CRC + SHA fields → save as `tools/fixtures/screenshots/phase1/{name}-legacy.png`
3. Open the same file in **modern** app → **Generate Key**
4. Screenshot → `tools/fixtures/screenshots/phase1/{name}-modern.png`
5. Mark Pass/Fail in the table below

Helper: `.\tools\manual_parity.ps1` prints expected values and exe paths.

## Sign-off

| Fixture | Date | Operator | Legacy CRC | Modern CRC | Legacy SHA | Modern SHA | Pass |
|---------|------|----------|------------|------------|------------|------------|------|
| digits.bin | 2026-07-07 | automated (dotnet test) | CBF43926 | CBF43926 | 67972355… | 67972355… | Pass |
| test.bin | 2026-07-07 | automated (dotnet test) | D87F7E0C | D87F7E0C | 0E6AD8B3… | 0E6AD8B3… | Pass |
| docx | | | A25E39C9 | | BB741E73… | | Pending manual screenshot |

Automated tests lock CRC/SHA for repo fixtures. Manual screenshots for legacy GUI are optional visual audit; docx row requires local file + operator sign-off.
