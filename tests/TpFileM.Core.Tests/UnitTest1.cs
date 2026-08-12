using System.Text.Json;
using TpFileM.Core;

namespace TpFileM.Core.Tests;

public class Crc32Tests
{
    [Fact]
    public void Empty_input_matches_zlib_crc()
    {
        Assert.Equal(0x00000000u, Crc32.Compute([]));
    }

    [Fact]
    public void Digits_matches_zlib_crc()
    {
        var data = System.Text.Encoding.ASCII.GetBytes("123456789");
        Assert.Equal(0xCBF43926u, Crc32.Compute(data));
    }
}

public class HasherTests
{
    [Fact]
    public void FormatShaKey_uses_little_endian_words()
    {
        var digest = new byte[20];
        BitConverter.TryWriteBytes(digest.AsSpan(0, 4), 0x67972355u);
        BitConverter.TryWriteBytes(digest.AsSpan(4, 4), 0xBD7D1290u);
        var formatted = Hasher.FormatShaKey(digest);
        Assert.Equal("67972355 BD7D1290 00000000 00000000 00000000", formatted);
    }
}

public class KeyGeneratorTests
{
    [Fact]
    public void GenerateFromBytes_roundtrip()
    {
        Assert.True(LegacySha1.IsAvailable, "Build TpFileM.LegacySha.Cli (win-x86) first.");

        var bytes = System.Text.Encoding.ASCII.GetBytes("test");
        var result = KeyGenerator.GenerateFromBytes("test.bin", bytes);
        Assert.Equal("D87F7E0C", result.CrcKey);
        Assert.Equal("0E6AD8B3 B29925F7 93802DA5 09E31588 4DB93485", result.ShaKey);
    }

    [Fact]
    public void GenerateFromPath_streaming_matches_buffer()
    {
        Assert.True(LegacySha1.IsAvailable, "Build TpFileM.LegacySha.Cli (win-x86) first.");

        var dir = Path.Combine(Path.GetTempPath(), "tpfilem-tests", Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(dir);
        var path = Path.Combine(dir, "digits.bin");
        File.WriteAllBytes(path, System.Text.Encoding.ASCII.GetBytes("123456789"));

        try
        {
            var streamed = KeyGenerator.GenerateFromPath(path);
            var buffered = KeyGenerator.GenerateFromBytes("digits.bin", File.ReadAllBytes(path));
            Assert.Equal(buffered.CrcKey, streamed.CrcKey);
            Assert.Equal(buffered.ShaKey, streamed.ShaKey);
            Assert.Equal("CBF43926", streamed.CrcKey);
        }
        finally
        {
            Directory.Delete(dir, recursive: true);
        }
    }
}

public class LegacyGoldenCrcTests
{
    private static readonly string RepoRoot = FindRepoRoot();
    private static readonly string FixturesDir = Path.Combine(RepoRoot, "tools", "fixtures");
    private static readonly string GoldenPath = Path.Combine(FixturesDir, "legacy-golden.json");

    [Fact]
    public void Fixture_vectors_match_golden_crc()
    {
        var golden = LoadGolden();
        foreach (var vector in golden.Vectors)
        {
            if (string.IsNullOrWhiteSpace(vector.Path))
            {
                var fixturePath = Path.Combine(FixturesDir, vector.File);
                Assert.True(File.Exists(fixturePath), $"Missing fixture: {fixturePath}");
                var bytes = File.ReadAllBytes(fixturePath);
                Assert.Equal(vector.Crc, Hasher.FormatCrcKey(Crc32.Compute(bytes)));
            }
        }
    }

    [Fact]
    public void Optional_external_docx_matches_golden_crc_when_present()
    {
        var golden = LoadGolden();
        var docx = golden.Vectors.FirstOrDefault(v => v.File.Contains("docx", StringComparison.OrdinalIgnoreCase));
        if (docx?.Path is null || !File.Exists(docx.Path))
        {
            return;
        }

        var bytes = File.ReadAllBytes(docx.Path);
        Assert.Equal(docx.Crc, Hasher.FormatCrcKey(Crc32.Compute(bytes)));
    }

    [Fact]
    public void Fixture_sha_matches_golden()
    {
        Assert.True(LegacySha1.IsAvailable, "Build TpFileM.LegacySha.Cli (win-x86) first.");

        var golden = LoadGolden();
        foreach (var vector in golden.Vectors.Where(v => !string.IsNullOrWhiteSpace(v.Sha)))
        {
            if (!string.IsNullOrWhiteSpace(vector.Path))
            {
                if (!File.Exists(vector.Path))
                {
                    continue;
                }

                var pathResult = KeyGenerator.GenerateFromPath(vector.Path);
                Assert.Equal(vector.Sha, pathResult.ShaKey);
                continue;
            }

            var fixturePath = Path.Combine(FixturesDir, vector.File);
            Assert.True(File.Exists(fixturePath), $"Missing fixture: {fixturePath}");
            var bytes = File.ReadAllBytes(fixturePath);
            var result = KeyGenerator.GenerateFromBytes(vector.File, bytes);
            Assert.Equal(vector.Sha, result.ShaKey);
        }
    }

    [Fact]
    public void Optional_external_docx_matches_golden_sha_when_present()
    {
        Assert.True(LegacySha1.IsAvailable, "Build TpFileM.LegacySha.Cli (win-x86) first.");

        var golden = LoadGolden();
        var docx = golden.Vectors.FirstOrDefault(v => v.File.Contains("docx", StringComparison.OrdinalIgnoreCase));
        if (docx?.Path is null || string.IsNullOrWhiteSpace(docx.Sha) || !File.Exists(docx.Path))
        {
            return;
        }

        var result = KeyGenerator.GenerateFromPath(docx.Path);
        Assert.Equal(docx.Sha, result.ShaKey);
    }

    private static GoldenFile LoadGolden()
    {
        var json = File.ReadAllText(GoldenPath);
        return JsonSerializer.Deserialize<GoldenFile>(json, JsonOptions()) ?? throw new InvalidOperationException("Invalid golden file.");
    }

    private static JsonSerializerOptions JsonOptions() => new()
    {
        PropertyNameCaseInsensitive = true,
    };

    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null)
        {
            var candidate = Path.Combine(dir.FullName, "tools", "fixtures", "legacy-golden.json");
            if (File.Exists(candidate))
            {
                return dir.FullName;
            }

            dir = dir.Parent;
        }

        throw new InvalidOperationException("Could not locate tools/fixtures/legacy-golden.json from test output directory.");
    }

    private sealed class GoldenFile
    {
        public List<GoldenVector> Vectors { get; set; } = [];
    }

    private sealed class GoldenVector
    {
        public string File { get; set; } = string.Empty;
        public string? Path { get; set; }
        public string Crc { get; set; } = string.Empty;
        public string? Sha { get; set; }
        public string? Note { get; set; }
    }
}
