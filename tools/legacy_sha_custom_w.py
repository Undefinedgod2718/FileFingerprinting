#!/usr/bin/env python3
"""TPFileM sha1_compress — Ghidra W schedule: W[i+13]=W[i+11]^W[i+6]^W[i-2]^W[i], no ROL."""
from __future__ import annotations

import struct
from pathlib import Path

GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"
MASK = 0xFFFFFFFF


def rol(x: int, n: int) -> int:
    return ((x & MASK) << n | (x & MASK) >> (32 - n)) & MASK


def expand_w(block16: list[int]) -> list[int]:
    w = [0, 0] + block16[:]
    for k in range(64):
        i = k - 2
        w.append((w[i + 11] ^ w[i + 6] ^ w[i - 2] ^ w[i]) & MASK)
    return w[2:]


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


def hash_bytes(data: bytes) -> list[int]:
    state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    bit = len(data) * 8
    blk = bytearray(64)
    blk[: len(data)] = data
    blk[len(data)] = 0x80
    struct.pack_into("<II", blk, 56, 0, bit)
    block = [struct.unpack_from("<I", blk, i)[0] for i in range(0, 64, 4)]
    compress(state, block)
    return state


def fmt(words: list[int]) -> str:
    return " ".join(f"{w:08X}" for w in words)


def main() -> None:
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    got = fmt(hash_bytes(raw))
    print("custom W", got)
    print("gui    ", GUI)
    print("match", got == GUI)


if __name__ == "__main__":
    main()
