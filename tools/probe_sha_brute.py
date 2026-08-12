#!/usr/bin/env python3
"""Brute SHA-1 block word byte-swap and length encodings for single-block inputs."""
import struct
from pathlib import Path

GUI = [0x67972355, 0xBD7D1290, 0x86D9DB6B, 0xFB4F59C8, 0xC3CEDDAD]
RAW = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
MASK = 0xFFFFFFFF


def rol(x: int, n: int) -> int:
    return ((x & MASK) << n | (x & MASK) >> (32 - n)) & MASK


def bswap32(x: int) -> int:
    x &= MASK
    return int.from_bytes(x.to_bytes(4, "little"), "big")


def expand_std(block16: list[int]) -> list[int]:
    w = block16[:]
    for i in range(16, 80):
        w.append(rol((w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]) & MASK, 1))
    return w


def compress(state: list[int], w: list[int]) -> None:
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


def hash_once(block_transform, length_pack) -> list[int]:
    state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    bit = len(RAW) * 8
    blk = bytearray(64)
    blk[: len(RAW)] = RAW
    blk[len(RAW)] = 0x80
    length_pack(blk, bit)
    words = [block_transform(struct.unpack_from("<I", blk, i)[0]) for i in range(0, 64, 4)]
    compress(state, expand_std(words))
    return state


def pack_be_q(blk: bytearray, bit: int) -> None:
    struct.pack_into(">Q", blk, 56, bit)


def pack_le_q(blk: bytearray, bit: int) -> None:
    struct.pack_into("<Q", blk, 56, bit)


def pack_le_ii(blk: bytearray, bit: int) -> None:
    struct.pack_into("<II", blk, 56, 0, bit)


def pack_be_ii(blk: bytearray, bit: int) -> None:
    struct.pack_into(">II", blk, 56, 0, bit)


def pack_hi_lo_le(blk: bytearray, bit: int) -> None:
    struct.pack_into("<II", blk, 56, 0, bit)  # same as le_ii


for name_t, tf in [("id", lambda x: x), ("bswap", bswap32)]:
    for name_l, lf in [
        ("be_q", pack_be_q),
        ("le_q", pack_le_q),
        ("be_ii", pack_be_ii),
        ("le_ii", pack_le_ii),
    ]:
        got = hash_once(tf, lf)
        if got == GUI:
            print("MATCH", name_t, name_l, got)

# legacy exact path output
print("done")
