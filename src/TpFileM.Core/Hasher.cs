using System.Text;

namespace TpFileM.Core;

public static class Hasher
{
    public static byte[] Sha1(ReadOnlySpan<byte> data) => LegacySha1.Compute(data);

    public static Sha1HashContext CreateSha1Context() => new();

    public static string FormatCrcKey(uint crc) => crc.ToString("X8");

    /// <summary>
    /// Legacy TPFileM format_sha_key: five LE uint32 words as %08X, space-separated.
    /// </summary>
    public static string FormatShaKey(ReadOnlySpan<byte> digest)
    {
        if (digest.Length != 20)
        {
            throw new ArgumentException("SHA-1 digest must be 20 bytes.", nameof(digest));
        }

        var sb = new StringBuilder(47);
        for (int i = 0; i < 5; i++)
        {
            if (i > 0)
            {
                sb.Append(' ');
            }

            uint word = BitConverter.ToUInt32(digest.Slice(i * 4, 4));
            sb.Append(word.ToString("X8"));
        }

        return sb.ToString();
    }
}

public sealed class Sha1HashContext : IDisposable
{
    private readonly MemoryStream _buffer = new();

    public void Update(ReadOnlySpan<byte> data)
    {
        _buffer.Write(data);
    }

    public byte[] Finalize()
    {
        byte[] all = _buffer.ToArray();
        _buffer.SetLength(0);
        return LegacySha1.Compute(all);
    }

    public void Dispose() => _buffer.Dispose();
}
