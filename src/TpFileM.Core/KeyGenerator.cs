namespace TpFileM.Core;

public enum KeyMode
{
    Legacy,
    Modern,
}

public sealed record KeyResult(string FileName, string CrcKey, string ShaKey);

public sealed class KeyGenerationException : Exception
{
    public KeyGenerationException(FilenameValidationResult reason)
        : base(FilenameValidationMessages.ToEnglish(reason))
    {
        Reason = reason;
    }

    public FilenameValidationResult Reason { get; }
}

public static class KeyGenerator
{
    private const int ChunkSize = 0x2000;

    public static KeyResult GenerateFromPath(string path, IProgress<HashProgress>? progress = null, CancellationToken cancellationToken = default)
    {
        var validation = FilenameValidator.ValidatePath(path);
        if (validation != FilenameValidationResult.Ok)
        {
            throw new KeyGenerationException(validation);
        }

        using var stream = File.OpenRead(path);
        long totalBytes = stream.Length;
        var crcCtx = Crc32.CreateContext();
        var buffer = new byte[ChunkSize];
        long processed = 0;

        int read;
        while ((read = stream.Read(buffer, 0, buffer.Length)) > 0)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var chunk = buffer.AsSpan(0, read);
            crcCtx.Update(chunk);
            processed += read;
            ReportProgress(progress, processed, totalBytes);
        }

        progress?.Report(new HashProgress(HashPhase.Done, 100, "Status_Done"));

        byte[] sha = LegacySha1.ComputeFile(path);

        return new KeyResult(
            Path.GetFileName(path),
            Hasher.FormatCrcKey(crcCtx.Finalize()),
            Hasher.FormatShaKey(sha));
    }

    public static KeyResult GenerateFromBytes(string displayName, ReadOnlySpan<byte> content)
    {
        if (string.IsNullOrWhiteSpace(displayName))
        {
            throw new KeyGenerationException(FilenameValidationResult.Empty);
        }

        uint crc = Crc32.Compute(content);
        byte[] sha = Hasher.Sha1(content);

        return new KeyResult(
            displayName,
            Hasher.FormatCrcKey(crc),
            Hasher.FormatShaKey(sha));
    }

    private static void ReportProgress(IProgress<HashProgress>? progress, long processed, long totalBytes)
    {
        if (progress is null)
        {
            return;
        }

        double percent = totalBytes > 0 ? processed * 100.0 / totalBytes : 100;
        progress.Report(new HashProgress(HashPhase.Reading, percent, "Status_Counting"));
    }
}
