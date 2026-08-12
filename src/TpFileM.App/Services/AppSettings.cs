using System.IO;
using System.Text.Json;

namespace TpFileM.App.Services;

public sealed class AppSettings
{
    public string Language { get; set; } = "en";
    public string? McpExePath { get; set; }

    private static string SettingsPath =>
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "TpFileM", "settings.json");

    public static AppSettings Load()
    {
        try
        {
            if (!File.Exists(SettingsPath))
            {
                return new AppSettings();
            }

            var json = File.ReadAllText(SettingsPath);
            return JsonSerializer.Deserialize<AppSettings>(json) ?? new AppSettings();
        }
        catch
        {
            return new AppSettings();
        }
    }

    public void Save()
    {
        var dir = Path.GetDirectoryName(SettingsPath)!;
        Directory.CreateDirectory(dir);
        var json = JsonSerializer.Serialize(this, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(SettingsPath, json);
    }

    public string ResolveMcpExePath()
    {
        if (!string.IsNullOrWhiteSpace(McpExePath) && File.Exists(McpExePath))
        {
            return McpExePath;
        }

        var sibling = Path.Combine(AppContext.BaseDirectory, "TpFileM.Mcp.exe");
        return File.Exists(sibling) ? sibling : string.Empty;
    }
}
