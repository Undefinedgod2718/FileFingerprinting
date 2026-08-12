using System.Buffers.Binary;
using System.Runtime.InteropServices;

namespace TpFileM.LegacySha.Cli;

internal static class PeImage
{
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr VirtualAlloc(
        IntPtr address,
        UIntPtr size,
        uint allocationType,
        uint protect);

    public static IntPtr MapPe(ReadOnlySpan<byte> pe)
    {
        if (pe.Length < 64 || pe[0] != (byte)'M' || pe[1] != (byte)'Z')
        {
            throw new InvalidDataException("Invalid MZ image.");
        }

        int peOffset = BinaryPrimitives.ReadInt32LittleEndian(pe.Slice(0x3C, 4));
        if (peOffset <= 0 || peOffset + 24 > pe.Length)
        {
            throw new InvalidDataException("Invalid PE header offset.");
        }

        ushort optionalHeaderSize = BinaryPrimitives.ReadUInt16LittleEndian(pe.Slice(peOffset + 20, 2));
        int optionalHeader = peOffset + 24;
        uint sizeOfImage = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(optionalHeader + 56, 4));
        int sectionCount = BinaryPrimitives.ReadUInt16LittleEndian(pe.Slice(peOffset + 6, 2));
        int sectionTable = optionalHeader + optionalHeaderSize;

        IntPtr baseAddr = VirtualAlloc(
            IntPtr.Zero,
            (UIntPtr)sizeOfImage,
            0x1000 | 0x2000,
            0x40);

        if (baseAddr == IntPtr.Zero)
        {
            throw new InvalidOperationException($"VirtualAlloc failed: {Marshal.GetLastWin32Error()}");
        }

        uint actualBase = (uint)baseAddr;
        uint preferredBase = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(optionalHeader + 28, 4));
        int dataDir = optionalHeader + 96 + 5 * 8;
        int relocRva = BinaryPrimitives.ReadInt32LittleEndian(pe.Slice(dataDir, 4));
        int relocSize = BinaryPrimitives.ReadInt32LittleEndian(pe.Slice(dataDir + 4, 4));

        unsafe
        {
            var image = new Span<byte>((void*)baseAddr, (int)sizeOfImage);
            image.Clear();

            for (int i = 0; i < sectionCount; i++)
            {
                int sec = sectionTable + i * 40;
                if (sec + 40 > pe.Length)
                {
                    break;
                }

                uint virtualSize = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(sec + 8, 4));
                uint virtualAddress = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(sec + 12, 4));
                uint rawSize = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(sec + 16, 4));
                uint rawPointer = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(sec + 20, 4));
                if (rawSize == 0)
                {
                    continue;
                }

                int copy = (int)Math.Min(rawSize, virtualSize == 0 ? rawSize : virtualSize);
                if (rawPointer + copy > pe.Length)
                {
                    throw new InvalidDataException("Section raw data out of range.");
                }

                pe.Slice((int)rawPointer, copy).CopyTo(image.Slice((int)virtualAddress, copy));
            }

            if (relocRva > 0 && relocSize > 0 && actualBase != preferredBase)
            {
                ApplyRelocations(image, pe, relocRva, relocSize, actualBase, preferredBase);
            }
        }

        return baseAddr;
    }

    private static void ApplyRelocations(
        Span<byte> image,
        ReadOnlySpan<byte> pe,
        int relocRva,
        int relocSize,
        uint actualBase,
        uint preferredBase)
    {
        int delta = unchecked((int)(actualBase - preferredBase));
        int offset = relocRva;
        int end = relocRva + relocSize;
        while (offset < end)
        {
            uint pageRva = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(offset, 4));
            uint blockSize = BinaryPrimitives.ReadUInt32LittleEndian(pe.Slice(offset + 4, 4));
            if (blockSize < 8)
            {
                break;
            }

            int count = ((int)blockSize - 8) / 2;
            for (int i = 0; i < count; i++)
            {
                ushort entry = BinaryPrimitives.ReadUInt16LittleEndian(pe.Slice(offset + 8 + i * 2, 2));
                int type = entry >> 12;
                int entryRva = (int)(pageRva + (entry & 0x0FFF));
                if (type == 3 && entryRva + 4 <= image.Length)
                {
                    int value = BinaryPrimitives.ReadInt32LittleEndian(image.Slice(entryRva, 4));
                    value += delta;
                    BinaryPrimitives.WriteInt32LittleEndian(image.Slice(entryRva, 4), value);
                }
            }

            offset += (int)blockSize;
        }
    }
}
