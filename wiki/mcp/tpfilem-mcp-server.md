# TpFileM MCP server

## Transport

stdio JSON-RPC (MCP subset implemented in `TpFileM.Mcp`)

## Tools

### `generate_key`

**Input**

```json
{ "file_path": "D:/path/to/file.bin" }
```

**Output** (text JSON in content)

```json
{
  "file_name": "file.bin",
  "crc_key": "49541D5A",
  "sha_key": "A9993E36 4706816A BA3E2571 7850C26C 9CD0D89D"
}
```

### `validate_filename`

**Input**

```json
{ "file_path": "D:/path/to/file.bin" }
```

**Output**

```json
{
  "valid": true,
  "result": "Ok",
  "message": ""
}
```

## Registration

See [build-mcp.md](../build/build-mcp.md).
