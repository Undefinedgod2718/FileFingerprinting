using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.Json;

namespace TpFileM.App.Services;

public static class McpSettingsService
{
    public static string BuildMcpJsonSnippet(string mcpExePath)
    {
        var normalized = mcpExePath.Replace('\\', '/');
        var payload = new
        {
            mcpServers = new Dictionary<string, object>
            {
                ["tpfilem"] = new { command = normalized, args = Array.Empty<string>() },
            },
        };

        return JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true });
    }

    public static async Task<(bool Ok, string Message)> SmokeTestAsync(string mcpExePath, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(mcpExePath) || !File.Exists(mcpExePath))
        {
            return (false, "MCP executable not found.");
        }

        using var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = mcpExePath,
                UseShellExecute = false,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
            },
        };

        if (!process.Start())
        {
            return (false, "Failed to start MCP process.");
        }

        var init = JsonSerializer.Serialize(new
        {
            jsonrpc = "2.0",
            id = 1,
            method = "initialize",
            @params = new { },
        });

        await process.StandardInput.WriteLineAsync(init.AsMemory(), cancellationToken);
        await process.StandardInput.FlushAsync(cancellationToken);

        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(5));

        try
        {
            var lineTask = process.StandardOutput.ReadLineAsync(timeout.Token);
            var line = await lineTask;
            if (string.IsNullOrWhiteSpace(line) || !line.Contains("\"result\"", StringComparison.Ordinal))
            {
                var err = await process.StandardError.ReadToEndAsync(timeout.Token);
                return (false, string.IsNullOrWhiteSpace(err) ? "No initialize response." : err.Trim());
            }

            return (true, "initialize ok");
        }
        catch (OperationCanceledException)
        {
            return (false, "Timed out waiting for MCP response.");
        }
        finally
        {
            try
            {
                if (!process.HasExited)
                {
                    process.Kill(entireProcessTree: true);
                }
            }
            catch
            {
                // ponytail: best-effort cleanup after smoke test
            }
        }
    }
}
