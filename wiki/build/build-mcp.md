# Build MCP server

## Run (stdio)

```powershell
dotnet run --project src/TpFileM.Mcp
```

## Cursor `mcp.json` example

```json
{
  "mcpServers": {
    "tpfilem": {
      "command": "dotnet",
      "args": [
        "run",
        "--project",
        "D:/Program_Coding/Q_Test/tpfilem-modern/src/TpFileM.Mcp/TpFileM.Mcp.csproj"
      ]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `generate_key` | `{ "file_path": "..." }` → CRC + SHA keys |
| `validate_filename` | `{ "file_path": "..." }` → validation result |

See [TpFileM MCP server](../mcp/tpfilem-mcp-server.md).
