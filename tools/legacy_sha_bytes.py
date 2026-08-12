#!/usr/bin/env python3
"""Byte-exact simulation of TPFileM SHA context (92 bytes = SUB ESP,0x5c)."""
from __future__ import annotations

import struct
from pathlib import Path

GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"
MASK = 0xFFFFFFFF


def rol(x: int, n: int) -> int:
    return ((x & MASK) << n | (x & MASK) >> (32 - n)) & MASK


def u32_le(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def p32_le(buf: bytearray, off: int, val: int) -> None:
    struct.pack_into("<I", buf, off, val & MASK)


def sha1_compress(ctx: bytearray) -> None:
    w = [u32_le(ctx, 0x1C + i * 4) for i in range(16)]
    for i in range(16, 80):
        w.append((w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]) & MASK)
        w[i] = rol(w[i], 1)
    a, b, c, d, e = (u32_le(ctx, i) for i in range(0, 20, 4))
    for i in range(80):
        if i < 20:
            f, k = (b & c) | (~b & d), 0x5A827999
        elif i < 40:
            f, k = b ^ c ^ d, 0x6ED9EBA1
        elif i < 60:
            f, k = (b & c) | (b & d) | (c & d), 0x8F1BBCDC
        else:
            f, k = b ^ c ^ d, 0xCA62C1D6
        temp = (rol(a, 5) + f + e + k + w[i]) & MASK
        e, d, c, b, a = d, c, rol(b, 30), a, temp
    p32_le(ctx, 0, (u32_le(ctx, 0) + a) & MASK)
    p32_le(ctx, 4, (u32_le(ctx, 4) + b) & MASK)
    p32_le(ctx, 8, (u32_le(ctx, 8) + c) & MASK)
    p32_le(ctx, 12, (u32_le(ctx, 12) + d) & MASK)
    p32_le(ctx, 16, (u32_le(ctx, 16) + e) & MASK)


def sha_init(ctx: bytearray) -> None:
    p32_le(ctx, 0, 0x67452301)
    p32_le(ctx, 4, 0xEFCDAB89)
    p32_le(ctx, 8, 0x98BADCFE)
    p32_le(ctx, 12, 0x10325476)
    p32_le(ctx, 16, 0xC3D2E1F0)
    p32_le(ctx, 0x14, 0)
    p32_le(ctx, 0x18, 0)


def sha_update(ctx: bytearray, data: bytes) -> None:
    n = len(data)
    lo = u32_le(ctx, 0x14)
    hi = u32_le(ctx, 0x18)
    new_lo = (lo + n * 8) & MASK
    if new_lo < lo:
        hi = (hi + 1) & MASK
    p32_le(ctx, 0x14, new_lo)
    p32_le(ctx, 0x18, (hi + (n >> 29)) & MASK)

    idx = 0
    if n > 0x3F:
        blocks = n >> 6
        rem = n - (blocks << 6)
        for _ in range(blocks):
            ctx[0x1C:0x5C] = data[idx : idx + 64]
            sha1_compress(ctx)
            idx += 64
        data = data[idx:]
        n = rem

    # MOVSD/MOVSB from EDI=[EBX+0x1c] — overwrite block from byte 0
    block = bytearray(64)
    block[:n] = data
    ctx[0x1C:0x5C] = block


def sha_final(ctx: bytearray) -> None:
    lo = u32_le(ctx, 0x14)
    hi = u32_le(ctx, 0x18)
    used = (lo >> 3) & 0x3F
    ctx[0x1C + used] = 0x80
    if used + 1 < 0x39:
        for i in range(used + 1, 0x38):
            ctx[0x1C + i] = 0
    else:
        for i in range(used + 1, 0x40):
            ctx[0x1C + i] = 0
        sha1_compress(ctx)
        ctx[0x1C:0x54] = b"\x00" * 56
    p32_le(ctx, 0x54, hi)
    p32_le(ctx, 0x58, lo)
    sha1_compress(ctx)


def fmt_ctx(ctx: bytearray) -> str:
    return " ".join(f"{u32_le(ctx, i):08X}" for i in range(0, 20, 4))


def main() -> None:
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    ctx = bytearray(0x5C)
    sha_init(ctx)
    sha_update(ctx, raw)
    sha_final(ctx)
    got = fmt_ctx(ctx)
    print("byte sim", got)
    print("gui     ", GUI)
    print("match", got == GUI)


if __name__ == "__main__":
    main()
