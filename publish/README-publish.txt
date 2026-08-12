File Fingerprinting — developer publish output
==============================================

GUI:  D:\Program_Coding\Q_Test\tpfilem-modern\tools\..\publish\app\FileFingerprinting.exe
MCP:  D:\Program_Coding\Q_Test\tpfilem-modern\tools\..\publish\app\TpFileM.Mcp.exe  (also copied next to GUI)
SHA:  D:\Program_Coding\Q_Test\tpfilem-modern\tools\..\publish\app\TpFileM.LegacySha.Cli.exe  (win-x86 legacy SHA helper)

End-user installer: see wiki/dev/ — run publish.ps1 -ForInstaller then build-installer.ps1

Cursor mcp.json example:
{
  "mcpServers": {
    "tpfilem": {
      "command": "D:/Program_Coding/Q_Test/tpfilem-modern/tools/../publish/app/TpFileM.Mcp.exe",
      "args": []
    }
  }
}
