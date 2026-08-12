# File Fingerprinting

**A modern file fingerprinting tool — for local use and your AI agents.**

---

File Fingerprinting is a local desktop application and AI-ready MCP server that generates precise cryptographic signatures (CRC-32 and custom legacy SHA) for files. Built to seamlessly replace legacy 32-bit `TPFileM.exe` workflows, it features a WPF GUI for human operators and a stdio MCP server for Claude and Cursor.

### WPF Desktop GUI
A fast, standalone 64-bit Windows desktop app built with WPF and .NET 8. Generates zlib CRC-32 and specialized SHA keys required for equipment verification workflows. 

### Legacy-Compatible Core
Under the hood, it orchestrates a dedicated `win-x86` native SHA helper to ensure 100% bit-for-bit parity with the legacy tools, seamlessly handling custom digest formats.

### Built for Agents (MCP)
A built-in stdio MCP server exposes fingerprinting tools to your local AI agents. Keep your codebase moving and let Claude Code or Cursor automatically call file fingerprinting actions directly on your machine.

## Quick start

```powershell
# Build the application
dotnet build

# Publish output to publish/app/
.\tools\publish.ps1
```

Run the GUI:
```powershell
.\publish\app\FileFingerprinting.exe
```

## MCP server

Configure your agent to use the MCP server directly from the publish output:

```json
{
  "mcpServers": {
    "file-fingerprinting": {
      "command": "path/to/publish/app/TpFileM.Mcp.exe",
      "args": []
    }
  }
}
```
