using System.Buffers.Binary;

namespace TpFileM.LegacySha.Cli;

internal static class Program
{
    private static string ResolveLegacyExe()
    {
        string installed = Path.Combine(AppContext.BaseDirectory, "runtime", "LegacyCore.exe");
        if (File.Exists(installed))
        {
            return installed;
        }

        string? fromEnv = Environment.GetEnvironmentVariable("TPFILEM_LEGACY_EXE");
        if (!string.IsNullOrWhiteSpace(fromEnv))
        {
            return fromEnv;
        }

        string flat = Path.Combine(AppContext.BaseDirectory, "TPFileM.exe");
        if (File.Exists(flat))
        {
            return flat;
        }

        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null)
        {
            var candidate = Path.Combine(dir.FullName, "TPFileM", "TPFileM.exe");
            if (File.Exists(candidate))
            {
                return candidate;
            }

            candidate = Path.GetFullPath(Path.Combine(dir.FullName, "..", "TPFileM", "TPFileM.exe"));
            if (File.Exists(candidate))
            {
                return candidate;
            }

            dir = dir.Parent;
        }

        throw new FileNotFoundException(
            "Legacy SHA runtime not found. Expected runtime\\LegacyCore.exe beside the app, or set TPFILEM_LEGACY_EXE (dev).");
    }

    public static int Main(string[] args)
    {
        try
        {
            string exePath;
            try
            {
                exePath = ResolveLegacyExe();
            }
            catch (FileNotFoundException ex)
            {
                Console.Error.WriteLine(ex.Message);
                return 2;
            }

            if (!File.Exists(exePath))
            {
                Console.Error.WriteLine($"Legacy core not found: {exePath}");
                return 2;
            }

            using var native = LegacyShaNative.LoadFromFile(exePath);
            byte[] data = ReadPayload(args);
            string formatted = LegacyShaNative.FormatDigest(native.Hash(data));
            Console.WriteLine(formatted);
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.Message);
            return 1;
        }
    }

    private static byte[] ReadPayload(string[] args)
    {
        if (args.Length >= 2 && args[0] == "--file")
        {
            return File.ReadAllBytes(args[1]);
        }

        if (args.Length >= 1 && args[0] == "--stdin")
        {
            Span<byte> hdr = stackalloc byte[4];
            if (Console.OpenStandardInput().Read(hdr) != 4)
            {
                throw new InvalidDataException("stdin length header required.");
            }

            int n = BinaryPrimitives.ReadInt32LittleEndian(hdr);
            if (n < 0)
            {
                throw new InvalidDataException("negative stdin length.");
            }

            if (n == 0)
            {
                return [];
            }

            var data = new byte[n];
            int read = 0;
            var stream = Console.OpenStandardInput();
            while (read < n)
            {
                int chunk = stream.Read(data, read, n - read);
                if (chunk <= 0)
                {
                    throw new EndOfStreamException("short stdin payload.");
                }

                read += chunk;
            }

            return data;
        }

        throw new InvalidOperationException("usage: LegacySha.Cli --stdin | --file <path>");
    }
}
