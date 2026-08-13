using System.Buffers.Binary;

namespace TpFileM.LegacySha.Cli;

internal static class Program
{
    private static void BackupToShared(string source, string dest, string sharedDir)
    {
        try
        {
            if (!Directory.Exists(sharedDir))
            {
                Directory.CreateDirectory(sharedDir);
            }
            if (!File.Exists(dest))
            {
                File.Copy(source, dest, overwrite: false);
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Warning: Failed to backup legacy core to shared directory: {ex.Message}");
        }
    }

    private static string ResolveLegacyExe()
    {
        string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string sharedDir = Path.Combine(localAppData, "FileFingerprinting", "Shared");
        string sharedExe = Path.Combine(sharedDir, "LegacyCore.exe");

        // 1. Check Shared first
        if (File.Exists(sharedExe))
        {
            return sharedExe;
        }

        // 2. Check current directory (and proactive backup)
        string installed = Path.Combine(AppContext.BaseDirectory, "runtime", "LegacyCore.exe");
        if (File.Exists(installed))
        {
            BackupToShared(installed, sharedExe, sharedDir);
            return installed;
        }

        // 3. Environment variable (dev)
        string? fromEnv = Environment.GetEnvironmentVariable("TPFILEM_LEGACY_EXE");
        if (!string.IsNullOrWhiteSpace(fromEnv) && File.Exists(fromEnv))
        {
            return fromEnv;
        }

        // 4. Flat structure
        string flat = Path.Combine(AppContext.BaseDirectory, "TPFileM.exe");
        if (File.Exists(flat))
        {
            BackupToShared(flat, sharedExe, sharedDir);
            return flat;
        }

        // 5. Velopack rescue scan: look in adjacent app-* folders
        var baseDir = new DirectoryInfo(AppContext.BaseDirectory);
        if (baseDir.Parent != null)
        {
            var appDirs = baseDir.Parent.GetDirectories("app-*")
                .OrderByDescending(d => d.Name)
                .ToList();
            
            foreach (var appDir in appDirs)
            {
                var candidate = Path.Combine(appDir.FullName, "runtime", "LegacyCore.exe");
                if (File.Exists(candidate))
                {
                    BackupToShared(candidate, sharedExe, sharedDir);
                    return sharedExe;
                }
                
                candidate = Path.Combine(appDir.FullName, "TPFileM.exe");
                if (File.Exists(candidate))
                {
                    BackupToShared(candidate, sharedExe, sharedDir);
                    return sharedExe;
                }
            }
        }

        // 6. Final fallback for legacy dev paths up the tree
        var dirUp = new DirectoryInfo(AppContext.BaseDirectory);
        while (dirUp != null)
        {
            var candidate = Path.Combine(dirUp.FullName, "TPFileM", "TPFileM.exe");
            if (File.Exists(candidate)) return candidate;

            candidate = Path.GetFullPath(Path.Combine(dirUp.FullName, "..", "TPFileM", "TPFileM.exe"));
            if (File.Exists(candidate)) return candidate;

            dirUp = dirUp.Parent;
        }

        throw new FileNotFoundException(
            $"Legacy SHA runtime not found. Please ensure LegacyCore.exe exists in {sharedDir}");
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
