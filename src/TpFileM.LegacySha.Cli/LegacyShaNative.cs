using System.Buffers.Binary;
using System.Runtime.InteropServices;

namespace TpFileM.LegacySha.Cli;

internal sealed class LegacyShaNative : IDisposable
{
    private const uint RvaShaInit = 0x1EF0;
    private const uint RvaShaUpdate = 0x1F30;
    private const uint RvaShaFinal = 0x1FD0;
    private const uint EcxGadgetRva = 0x5000;

    private readonly IntPtr _image;
    private readonly uint _imageBase;
    private readonly ShaInitDelegate _init;
    private readonly ShaUpdateDelegate _update;
    private readonly IntPtr _finalFn;
    private readonly IntPtr _ecxGadget;

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    private delegate void ShaInitDelegate(IntPtr ctx);

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    private delegate void ShaUpdateDelegate(IntPtr ctx, IntPtr data, uint length);

    private LegacyShaNative(IntPtr image)
    {
        _image = image;
        _imageBase = (uint)image;
        _init = Marshal.GetDelegateForFunctionPointer<ShaInitDelegate>(Fn(RvaShaInit));
        _update = Marshal.GetDelegateForFunctionPointer<ShaUpdateDelegate>(Fn(RvaShaUpdate));
        _finalFn = Fn(RvaShaFinal);
        _ecxGadget = (IntPtr)(_imageBase + EcxGadgetRva);
    }

    private IntPtr Fn(uint rva) => (IntPtr)(_imageBase + rva);

    public static LegacyShaNative LoadFromFile(string path)
    {
        byte[] pe = File.ReadAllBytes(path);
        IntPtr image = PeImage.MapPe(pe);
        return new LegacyShaNative(image);
    }

    public byte[] Hash(ReadOnlySpan<byte> data)
    {
        IntPtr ctx = Marshal.AllocHGlobal(0x5C);
        try
        {
            unsafe
            {
                new Span<byte>((void*)ctx, 0x5C).Clear();
            }

            _init(ctx);

            const int chunk = 0x2000;
            if (!data.IsEmpty)
            {
                for (int offset = 0; offset < data.Length; offset += chunk)
                {
                    int len = Math.Min(chunk, data.Length - offset);
                    IntPtr buf = Marshal.AllocHGlobal(len);
                    try
                    {
                        Marshal.Copy(data.Slice(offset, len).ToArray(), 0, buf, len);
                        _update(ctx, buf, (uint)len);
                    }
                    finally
                    {
                        Marshal.FreeHGlobal(buf);
                    }
                }
            }

            X86Thunk.InvokeFinal(ctx, _ecxGadget, _finalFn);

            var digest = new byte[20];
            Marshal.Copy(ctx, digest, 0, 20);
            return digest;
        }
        finally
        {
            Marshal.FreeHGlobal(ctx);
        }
    }

    public static string FormatDigest(ReadOnlySpan<byte> digest)
    {
        if (digest.Length != 20)
        {
            throw new ArgumentException("Digest must be 20 bytes.", nameof(digest));
        }

        Span<uint> words = stackalloc uint[5];
        for (int i = 0; i < 5; i++)
        {
            words[i] = BinaryPrimitives.ReadUInt32LittleEndian(digest.Slice(i * 4, 4));
        }

        return string.Join(' ', words.ToArray().Select(w => w.ToString("X8")));
    }

    public void Dispose()
    {
        // ponytail: image stays mapped for process lifetime
    }
}
