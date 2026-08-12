namespace TpFileM.Core;

/// <summary>
/// PKZIP / zlib CRC-32 as shown by Delta TPFileM GUI (IEEE reflected, poly 0xEDB88320).
/// </summary>
public static class Crc32
{
    public static uint Compute(ReadOnlySpan<byte> data)
    {
        var ctx = CreateContext();
        ctx.Update(data);
        return ctx.Finalize();
    }

    public static Crc32Context CreateContext() => new();
}

public sealed class Crc32Context
{
    private System.IO.Hashing.Crc32 _crc = new();

    public void Update(ReadOnlySpan<byte> data) => _crc.Append(data);

    public uint Finalize() => _crc.GetCurrentHashAsUInt32();
}
