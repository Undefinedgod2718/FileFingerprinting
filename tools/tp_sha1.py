#!/usr/bin/env python3
"""TPFileM SHA-1: W[-2]=bitlen_lo on stack, W[k+13] XOR expand, block at W[2..17]."""
from __future__ import annotations

import struct
from pathlib import Path

MASK = 0xFFFFFFFF


def rol(x: int, n: int) -> int:
    return ((x & MASK) << n | (x & MASK) >> (32 - n)) & MASK


def _w(w: list[int], w_m2: int, w_m1: int, i: int) -> int:
    if i == -2:
        return w_m2 & MASK
    if i == -1:
        return w_m1 & MASK
    return w[i] & MASK


def expand_w(block16: list[int], w_m2: int, w_m1: int = 0) -> list[int]:
    w = [0, 0] + [x & MASK for x in block16]
    for k in range(64):
        target = k + 13
        if target >= len(w):
            w.extend([0] * (target - len(w) + 1))
        w[target] = (
            _w(w, w_m2, w_m1, k + 11)
            ^ _w(w, w_m2, w_m1, k + 6)
            ^ _w(w, w_m2, w_m1, k - 2)
            ^ _w(w, w_m2, w_m1, k)
        ) & MASK
    while len(w) < 80:
        w.append(0)
    return w[:80]


def compress(state: list[int], block16: list[int], bitlen_lo: int) -> None:
    w = expand_w(block16, bitlen_lo, 0)
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


def tp_sha1(data: bytes) -> list[int]:
    state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    lo = len(data) * 8
    hi = 0
    buf = bytearray(64)
    buf[: len(data)] = data
    used = len(data)
    buf[used] = 0x80
    if used + 1 < 0x38:
        for i in range(used + 1, 0x38):
            buf[i] = 0
    else:
        raise NotImplementedError("ponytail: large file path needs streaming compress")
    struct.pack_into("<II", buf, 56, hi, lo)
    block = [struct.unpack_from("<I", buf, i)[0] for i in range(0, 64, 4)]
    compress(state, block, lo)
    return state


def format_sha(words: list[int]) -> str:
    return " ".join(f"{w:08X}" for w in words)


if __name__ == "__main__":
    gui = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    got = format_sha(tp_sha1(raw))
    print(got, got == gui)
