using System.Text.Json;
using System.Text.Json.Serialization;
using TpFileM.Core;

namespace TpFileM.Mcp;

internal static class Program
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    public static async Task Main()
    {
        string? line;
        while ((line = await Console.In.ReadLineAsync()) is not null)
        {
            if (string.IsNullOrWhiteSpace(line))
            {
                continue;
            }

            using var doc = JsonDocument.Parse(line);
            var root = doc.RootElement;
            if (!root.TryGetProperty("method", out var methodEl))
            {
                continue;
            }

            var id = root.TryGetProperty("id", out var idEl) ? idEl.Clone() : default;
            var method = methodEl.GetString() ?? string.Empty;
            object? result = method switch
            {
                "initialize" => new
                {
                    protocolVersion = "2024-11-05",
                    capabilities = new { tools = new { } },
                    serverInfo = new { name = "tpfilem-mcp", version = "1.0.0" },
                },
                "tools/list" => new
                {
                    tools = new object[]
                    {
                        new
                        {
                            name = "generate_key",
                            description = "Generate CRC and SHA keys for a file path.",
                            inputSchema = new
                            {
                                type = "object",
                                properties = new { file_path = new { type = "string", description = "Absolute path to input file" } },
                                required = new[] { "file_path" },
                            },
                        },
                        new
                        {
                            name = "validate_filename",
                            description = "Validate whether a file path passes legacy filename checks.",
                            inputSchema = new
                            {
                                type = "object",
                                properties = new { file_path = new { type = "string", description = "Absolute path to input file" } },
                                required = new[] { "file_path" },
                            },
                        },
                    },
                },
                "tools/call" => HandleToolCall(root),
                _ => null,
            };

            if (result is null && method is not ("notifications/initialized"))
            {
                WriteResponse(id, error: new { code = -32601, message = $"Method not found: {method}" });
                continue;
            }

            if (result is not null)
            {
                WriteResponse(id, result);
            }
        }
    }

    private static object HandleToolCall(JsonElement root)
    {
        var args = root.GetProperty("params");
        var name = args.GetProperty("name").GetString() ?? string.Empty;
        var input = args.TryGetProperty("arguments", out var argEl)
            ? argEl
            : default;

        return name switch
        {
            "generate_key" => ToolText(HandleGenerateKey(input)),
            "validate_filename" => ToolText(HandleValidate(input)),
            _ => ToolText($"Unknown tool: {name}", isError: true),
        };
    }

    private static string HandleGenerateKey(JsonElement input)
    {
        var path = input.GetProperty("file_path").GetString() ?? string.Empty;
        try
        {
            var result = KeyGenerator.GenerateFromPath(path);
            return JsonSerializer.Serialize(new
            {
                file_name = result.FileName,
                crc_key = result.CrcKey,
                sha_key = result.ShaKey,
            }, JsonOptions);
        }
        catch (KeyGenerationException ex)
        {
            return JsonSerializer.Serialize(new { error = ex.Message, reason = ex.Reason.ToString() }, JsonOptions);
        }
    }

    private static string HandleValidate(JsonElement input)
    {
        var path = input.GetProperty("file_path").GetString() ?? string.Empty;
        var result = FilenameValidator.ValidatePath(path);
        return JsonSerializer.Serialize(new
        {
            valid = result == FilenameValidationResult.Ok,
            result = result.ToString(),
            message = FilenameValidationMessages.ToEnglish(result),
        }, JsonOptions);
    }

    private static object ToolText(string text, bool isError = false) => new
    {
        content = new[] { new { type = "text", text } },
        isError,
    };

    private static void WriteResponse(JsonElement id, object? result = null, object? error = null)
    {
        var payload = new Dictionary<string, object?> { ["jsonrpc"] = "2.0", ["id"] = id.ValueKind == JsonValueKind.Undefined ? null : JsonSerializer.Deserialize<object>(id.GetRawText()) };
        if (error is not null)
        {
            payload["error"] = error;
        }
        else
        {
            payload["result"] = result;
        }

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
    }
}
