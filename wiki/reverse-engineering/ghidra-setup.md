# Ghidra setup

## Status

During initial RE, **no Ghidra MCP instance was running**. Static analysis was performed with **Capstone** (Python) scripts under `tools/`.

## Recommended setup

1. Install Ghidra and enable the `user-ghidra` MCP server in Cursor
2. Import legacy binary:

   ```
   D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe
   ```

3. Language: `x86:LE:32:default`
4. Start from string xrefs:
   - `CRC Counting ..` → `0x004019C0`
   - `SHA Counting ..` → `0x00402060`
   - `File name Error in SHA!` → `0x00402246`

## Helper scripts

| Script | Output |
|--------|--------|
| `tools/disasm_probe.py` | Initial region dump |
| `tools/disasm_key_funcs.py` | CRC/SHA/generate-key regions |
| `tools/disasm_validate.py` | Validation + SHA wrapper |
| `tools/find_crypto.py` | String push sites, SHA-1 constants |

Raw notes: `tools/ghidra_notes/`
