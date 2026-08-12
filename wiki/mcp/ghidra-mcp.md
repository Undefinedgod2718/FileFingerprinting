# Ghidra MCP

Use when a Ghidra instance is running and `user-ghidra` MCP is connected.

## Workflow

1. `list_instances` — confirm connection
2. `import_file` with `D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe`
3. Follow xrefs from strings listed in [function-map.md](../reverse-engineering/function-map.md)

## Fallback

If Ghidra is unavailable, use Python scripts in `tools/` (Capstone).
