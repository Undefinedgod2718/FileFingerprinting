#!/usr/bin/env python3
"""Port legacy SHA-1 from Ghidra decompile (FUN_00401ef0/1f30/1fd0/01ce0)."""
from __future__ import annotations

import struct
from pathlib import Path

MASK = 0xFFFFFFFF


def rol(x: int, n: int) -> int:
    x &= MASK
    return ((x << n) | (x >> (32 - n))) & MASK


def sha1_compress(state: list[int], block: list[int]) -> None:
    w = block[:16]
    for i in range(16, 80):
        w.append((w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]) & MASK)
        w[i] = rol(w[i], 1)

    a, b, c, d, e = state
    for i in range(80):
        if i < 20:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif i < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        temp = (rol(a, 5) + f + e + k + w[i]) & MASK
        e = d
        d = c
        c = rol(b, 30)
        b = a
        a = temp
    state[0] = (state[0] + a) & MASK
    state[1] = (state[1] + b) & MASK
    state[2] = (state[2] + c) & MASK
    state[3] = (state[3] + d) & MASK
    state[4] = (state[4] + e) & MASK


class LegacySha1:
    def __init__(self) -> None:
        self.state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
        self.bitlen_lo = 0
        self.bitlen_hi = 0
        self.buf = bytearray(64)
        self.buf_used = 0

    def update(self, data: bytes) -> None:
        i = 0
        while i < len(data):
            take = min(64 - self.buf_used, len(data) - i)
            self.buf[self.buf_used : self.buf_used + take] = data[i : i + take]
            self.buf_used += take
            i += take

            bit_add = take * 8
            new_lo = (self.bitlen_lo + bit_add) & MASK
            if new_lo < self.bitlen_lo:
                self.bitlen_hi = (self.bitlen_hi + 1) & MASK
            self.bitlen_lo = new_lo
            self.bitlen_hi = (self.bitlen_hi + (take >> 29)) & MASK

            if self.buf_used == 64:
                block = list(struct.unpack(">16I", self.buf))
                sha1_compress(self.state, block)
                self.buf_used = 0

    def finalize(self) -> list[int]:
        total_bits = (self.bitlen_hi, self.bitlen_lo)
        self.buf[self.buf_used] = 0x80
        self.buf_used += 1
        if self.buf_used > 56:
            self.buf[self.buf_used : 64] = b"\x00" * (64 - self.buf_used)
            block = list(struct.unpack(">16I", self.buf))
            sha1_compress(self.state, block)
            self.buf_used = 0
        self.buf[self.buf_used : 56] = b"\x00" * (56 - self.buf_used)
        self.buf[56:64] = struct.pack(">II", total_bits[0], total_bits[1])
        block = list(struct.unpack(">16I", self.buf))
        sha1_compress(self.state, block)
        return self.state[:]

    def format_gui(self) -> str:
        return " ".join(f"{w:08X}" for w in self.finalize())


def main() -> None:
    data = Path(__file__).resolve().parent / "fixtures" / "digits.bin"
    raw = data.read_bytes()
    h = LegacySha1()
    h.update(raw)
    print("legacy port", h.format_gui())
    print("gui golden", "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD")


if __name__ == "__main__":
    main()
