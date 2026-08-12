#!/usr/bin/env python3
"""sha1_compress expansion: W[i+14]=W[i+11]^W[i+6]^W[i-2]^W[i] (no ROL), 64 iters from i=2."""
from __future__ import annotations

import struct
from pathlib import Path

GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"
MASK = 0xFFFFFFFF


def rol(x: int, n: int) -> int:
    return ((x & MASK) << n | (x & MASK) >> (32 - n)) & MASK


def expand_w(block16: list[int]) -> list[int]:
    w = [0] * 80
    w[:16] = block16
    for j in range(64):
        i = 2 + j
        w[i + 14] = (w[i + 11] ^ w[i + 6] ^ w[i - 2] ^ w[i]) & MASK
    return w


def compress(state: list[int], block16: list[int]) -> None:
    w = expand_w(block16)
    a, b, c, d, e = state
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
    state[:] = [(state[i] + v) & MASK for i, v in enumerate([a, b, c, d, e])]


def u32le(buf: bytes, o: int) -> int:
    return struct.unpack_from("<I", buf, o)[0]


def hash_legacy_pipeline(data: bytes) -> list[int]:
    ctx = bytearray(0x5C)
    struct.pack_into("<5I", ctx, 0, 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)
    lo = len(data) * 8
    hi = 0
    struct.pack_into("<II", ctx, 0x14, lo, hi)

    # update tail
    blk = bytearray(64)
    blk[: len(data)] = data
    ctx[0x1C:0x5C] = blk

    # finalize
    used = (lo >> 3) & 0x3F
    buf = bytearray(ctx[0x1C:0x5C])
    buf[used] = 0x80
    if used + 1 < 0x39:
        for i in range(used + 1, 0x38):
            buf[i] = 0
    else:
        for i in range(used + 1, 0x40):
            buf[i] = 0
        block = [u32le(buf, i * 4) for i in range(16)]
        state = list(struct.unpack_from("<5I", ctx, 0))
        compress(state, block)
        struct.pack_into("<5I", ctx, 0, *state)
        buf = bytearray(64)
    struct.pack_into("<II", buf, 56, hi, lo)
    block = [u32le(buf, i * 4) for i in range(16)]
    state = list(struct.unpack_from("<5I", ctx, 0))
    compress(state, block)
    return state


def main() -> None:
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    got = " ".join(f"{w:08X}" for w in hash_legacy_pipeline(raw))
    print(got)
    print(GUI)
    print(got == GUI)


if __name__ == "__main__":
    main()
