using System.IO;
using System.Reflection;
using System.Text.Json;
using System.Windows;
using TpFileM.Core;

namespace TpFileM.App.Services;

public sealed class LocalizationService
{
    private readonly Dictionary<string, string> _strings;

    public LocalizationService(AppSettings settings)
    {
        Language = NormalizeLanguage(settings.Language);
        _strings = LoadStrings(Language);
    }

    public string Language { get; }

    public string Get(string key)
    {
        if (_strings.TryGetValue(key, out var value))
        {
            return value;
        }

        return key;
    }

    public string Format(string key, params object[] args) => string.Format(Get(key), args);

    public string ValidationMessage(FilenameValidationResult result)
    {
        var key = FilenameValidationMessages.ToMessageKey(result);
        return string.IsNullOrEmpty(key) ? string.Empty : Get(key);
    }

    public FlowDirection FlowDirection => Language == "zh-TW" ? FlowDirection.LeftToRight : FlowDirection.LeftToRight;

    private static string NormalizeLanguage(string? language) =>
        language?.Equals("zh-TW", StringComparison.OrdinalIgnoreCase) == true ? "zh-TW" : "en";

    private static Dictionary<string, string> LoadStrings(string language)
    {
        var assembly = Assembly.GetExecutingAssembly();
        using var stream = OpenResourceStream(assembly, language);
        if (stream is null)
        {
            return new Dictionary<string, string>();
        }

        using var reader = new StreamReader(stream);
        var json = reader.ReadToEnd();
        return JsonSerializer.Deserialize<Dictionary<string, string>>(json) ?? new Dictionary<string, string>();
    }

    private static Stream? OpenResourceStream(Assembly assembly, string language)
    {
        var suffix = language == "zh-TW"
            ? "Assets.strings-zh-TW.json"
            : "Assets.strings-en.json";

        var resourceName = $"{assembly.GetName().Name}.{suffix}";
        var stream = assembly.GetManifestResourceStream(resourceName);
        if (stream is not null)
        {
            return stream;
        }

        foreach (var name in assembly.GetManifestResourceNames())
        {
            if (name.EndsWith(suffix, StringComparison.OrdinalIgnoreCase))
            {
                return assembly.GetManifestResourceStream(name);
            }
        }

        return null;
    }
}
