#!/usr/bin/env python3
"""Reference port of TPFileM legacy SHA-1 (for C# parity)."""
from __future__ import annotations

import struct
from pathlib import Path

MASK = 0xFFFFFFFF
H0 = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]


def rol(x: int, n: int) -> int:
    x &= MASK
    return ((x << n) | (x >> (32 - n))) & MASK


def expand_w(block16: list[int], w_m2: int) -> list[int]:
    w = [0, 0] + [x & MASK for x in block16]
    for k in range(64):
        t = k + 14
        if t >= len(w):
            w.extend([0] * (t - len(w) + 1))

        def gw(i: int) -> int:
            if i == -2:
                return w_m2 & MASK
            if i == -1:
                return 0
            return w[i] & MASK

        w[t] = (gw(k + 11) ^ gw(k + 6) ^ gw(k - 2) ^ gw(k)) & MASK
    while len(w) < 82:
        w.append(0)
    return w


def rounds(w: list[int], state: list[int]) -> None:
    a, b, c, d, e = state
    for i in range(80):
        wi = w[i + 2]
        if i < 20:
            f, k = (b & c) | ((~b) & d) & MASK, 0x5A827999
        elif i < 40:
            f, k = b ^ c ^ d, 0x6ED9EBA1
        elif i < 60:
            f, k = (b & c) | (b & d) | (c & d), 0x8F1BBCDC
        else:
            f, k = b ^ c ^ d, 0xCA62C1D6
        temp = (rol(a, 5) + f + e + k + wi) & MASK
        e, d, c, b, a = d, c, rol(b, 30), a, temp
    state[:] = [(state[i] + v) & MASK for i, v in enumerate([a, b, c, d, e])]


def compress(state: list[int], block: bytes, bitlen_lo: int) -> None:
    block16 = [struct.unpack_from("<I", block, i)[0] for i in range(0, 64, 4)]
    w = expand_w(block16, bitlen_lo)
    rounds(w, state)


class Ctx:
    def __init__(self) -> None:
        self.state = list(H0)
        self.bitlen_lo = 0
        self.bitlen_hi = 0
        self.buf = bytearray(64)

    def _add_len(self, nbytes: int) -> None:
        bits = nbytes * 8
        lo = self.bitlen_lo + bits
        hi = self.bitlen_hi
        if lo < self.bitlen_lo:
            hi += 1
        carry = bits >> 29
        self.bitlen_lo = lo & MASK
        self.bitlen_hi = (hi + carry) & MASK

    def partial_len(self) -> int:
        return (self.bitlen_lo >> 3) & 0x3F

    def update(self, data: bytes) -> None:
        if not data:
            return
        self._add_len(len(data))
        bitlen_lo = self.bitlen_lo
        if len(data) >= 64:
            offset = 0
            while len(data) - offset >= 64:
                compress(self.state, data[offset : offset + 64], bitlen_lo)
                offset += 64
            rem = len(data) - offset
            self.buf[:rem] = data[offset:]
            for i in range(rem, 64):
                self.buf[i] = 0
        else:
            self.buf[: len(data)] = data
            for i in range(len(data), 64):
                self.buf[i] = 0

    def final(self) -> list[int]:
        total_lo = self.bitlen_lo
        total_hi = self.bitlen_hi
        idx = self.partial_len()
        self.buf[idx] = 0x80
        idx += 1

        if idx > 0x38:
            while idx < 64:
                self.buf[idx] = 0
                idx += 1
            compress(self.state, bytes(self.buf), total_lo)
            for i in range(64):
                self.buf[i] = 0
            idx = 0

        while idx < 0x38:
            self.buf[idx] = 0
            idx += 1

        struct.pack_into("<I", self.buf, 0x38, total_hi)
        struct.pack_into("<I", self.buf, 0x3C, total_lo)
        compress(self.state, bytes(self.buf), total_lo)
        return list(self.state)


def hash_bytes(data: bytes) -> str:
    ctx = Ctx()
    chunk = 0x2000
    if not data:
        pass
    else:
        for i in range(0, len(data), chunk):
            ctx.update(data[i : i + chunk])
    return " ".join(f"{w:08X}" for w in ctx.final())


if __name__ == "__main__":
    from unicorn_sha import run_sha

    fixtures = Path(__file__).resolve().parent / "fixtures"
    for name in ["empty.bin", "digits.bin", "test.bin", "seq16.bin"]:
        raw = (fixtures / name).read_bytes()
        ref = hash_bytes(raw)
        uni = run_sha(raw)
        print(name, ref == uni)
        if ref != uni:
            print("  ref", ref)
            print("  uni", uni)
