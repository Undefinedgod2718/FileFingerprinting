# Function map

| VA | Role |
|----|------|
| `0x00401790` | Build CRC lookup table (poly `0x04C11DB7`) |
| `0x004019C0` | CRC over file handle (8 KiB reads) |
| `0x00401C30` | Generate CRC key string (`%08X`) into dialog field |
| `0x00401CE0` | SHA-1 compression |
| `0x00402060` | SHA over file with progress/status |
| `0x004021A0` | Format SHA digest (`%08X` × 5) |
| `0x004021F0` | **Generate Key** button handler |
| `0x004013B1` | Initial status message on file select |

## String RVAs and xrefs (MCP-verified 2026-07-06)

After `connect_instance("SC")` + `run_analysis`, use `search_strings` / `get_xrefs_to`. UI error strings are not always in Ghidra’s string table until defined; use `search_byte_patterns` for little-endian VAs or see `tools/ghidra_notes/string_push_sites.txt`.

| VA | Text | Xref sites |
|----|------|------------|
| `0x41D0B0` | `Step #1: Please select a file or drag and drop.` | `0x004013B1` (`FUN_004012d0`) |
| `0x41D0FC` | `Step #2: Press Generate Key button.` | `0x00401918`, `0x00401BDE` |
| `0x41D148` | `CRC Counting ..` | `0x004019E5`, `0x00401AC8` (`crc_compute_file`) |
| `0x41D158` | `%08X` | `0x00401CA9` |
| `0x41D160` | `Step #1: File name Error! …` | `0x00401C74` (byte pattern `60 D1 41 00`) |
| `0x41D1AC` | `SHA Counting ..` | `0x00402085`, `0x0040214C` (`sha_compute_file`) |
| `0x41D1BC` | `%08X %08X %08X %08X %08X` | `0x004021C1` |
| `0x41D1D8` | `OK! Keys are generated! …` | `0x0040226D` (byte pattern `D8 D1 41 00`) |
| `0x41D228` | `Step #1: File name Error in SHA! …` | `0x00402246` (byte pattern `28 D2 41 00`) |
