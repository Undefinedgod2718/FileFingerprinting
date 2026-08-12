using System.Diagnostics;
using System.Text;

namespace TpFileM.Core;

/// <summary>
/// TPFileM legacy SHA-1 via x86 native helper (maps TPFileM.exe SHA routines).
/// </summary>
public static class LegacySha1
{
    public static bool IsAvailable => FindHelper() is not null;

    public static byte[] Compute(ReadOnlySpan<byte> data)
    {
        string? helper = FindHelper()
            ?? throw new InvalidOperationException("TpFileM.LegacySha.Cli.exe not found.");

        using var process = StartHelper(helper, $"--stdin");
        process.StandardInput.BaseStream.Write(BitConverter.GetBytes(data.Length));
        if (!data.IsEmpty)
        {
            process.StandardInput.BaseStream.Write(data);
        }

        process.StandardInput.Close();
        return ReadDigest(process);
    }

    public static byte[] ComputeFile(string path)
    {
        string? helper = FindHelper()
            ?? throw new InvalidOperationException("TpFileM.LegacySha.Cli.exe not found.");

        using var process = StartHelper(helper, $"--file \"{path}\"");
        return ReadDigest(process);
    }

    private static Process StartHelper(string helper, string args)
    {
        var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = helper,
                Arguments = args,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8,
            },
        };

        if (!process.Start())
        {
            throw new InvalidOperationException("Failed to start legacy SHA helper.");
        }

        return process;
    }

    private static byte[] ReadDigest(Process process)
    {
        string line = process.StandardOutput.ReadLine()
            ?? throw new InvalidOperationException("Legacy SHA helper produced no output.");
        process.WaitForExit();
        if (process.ExitCode != 0)
        {
            string err = process.StandardError.ReadToEnd();
            throw new InvalidOperationException($"Legacy SHA helper failed: {err}");
        }

        return ParseWords(line);
    }

    private static byte[] ParseWords(string formatted)
    {
        var parts = formatted.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length != 5)
        {
            throw new InvalidOperationException($"Expected 5 SHA words, got: {formatted}");
        }

        var digest = new byte[20];
        for (int i = 0; i < 5; i++)
        {
            uint word = Convert.ToUInt32(parts[i], 16);
            BitConverter.TryWriteBytes(digest.AsSpan(i * 4, 4), word);
        }

        return digest;
    }

    private static string? FindHelper()
    {
        foreach (string name in new[] { "TpFileM.LegacySha.Cli.exe", "LegacySha.Cli.exe" })
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir is not null)
            {
                var candidate = Path.Combine(dir.FullName, name);
                if (File.Exists(candidate))
                {
                    return candidate;
                }

                candidate = Path.Combine(
                    dir.FullName,
                    "src",
                    "TpFileM.LegacySha.Cli",
                    "bin",
                    "Release",
                    "net10.0",
                    "win-x86",
                    "publish",
                    "TpFileM.LegacySha.Cli.exe");
                if (File.Exists(candidate))
                {
                    return candidate;
                }

                dir = dir.Parent;
            }
        }

        return null;
    }
}
