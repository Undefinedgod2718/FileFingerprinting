# Binary overview

## PE summary

| Field | Value |
|-------|-------|
| Machine | i386 (32-bit) |
| Subsystem | GUI |
| Image base | `0x00400000` |
| Size | 143,360 bytes |
| Sections | `.text`, `.rdata`, `.data`, `.rsrc` |

## Key imports

- `KERNEL32.dll` — file I/O (`CreateFileA`, `ReadFile`)
- `USER32.dll` — dialog UI
- `ADVAPI32.dll` — registry (not replicated in modern app)
- `comdlg32.dll` — file open dialog

## UI strings (from resources)

- Window: `Telecom Power File Monitor v1.0`
- Fields: `File name`, `CRC Key`, `SHA Key`
- Buttons: `Generate Key`, `Select a file`, `Quit`

## Raw RE artifacts

- `tools/ghidra_notes/disasm_regions.txt`
- `tools/ghidra_notes/key_functions.txt`
- `tools/ghidra_notes/string_push_sites.txt`
- `tools/ghidra_notes/validate_and_sha.txt`
