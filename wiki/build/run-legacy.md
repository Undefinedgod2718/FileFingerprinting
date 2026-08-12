# Run legacy binary

```powershell
& "D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe"
```

## Parallel comparison

1. Run `tools/legacy_probe.ps1` to create fixtures under `tools/fixtures/`
2. Open legacy app → select each fixture → **Generate Key**
3. Compare with `dotnet test` / modern GUI output

| Fixture | Expected CRC (zlib / GUI) |
|---------|---------------------------|
| `empty.bin` | `00000000` |
| `digits.bin` | `CBF43926` |
| `test.bin` | `D87F7E0C` |
| `seq16.bin` | `CECEE288` |

Manual checklist: [`wiki/testing/manual-gui-parity.md`](../testing/manual-gui-parity.md)
