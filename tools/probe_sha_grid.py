#!/usr/bin/env python3
"""Grid-search SHA-1 block/length endian combos vs GUI golden."""
import hashlib
import struct
from pathlib import Path

GUI = [0x67972355, 0xBD7D1290, 0x86D9DB6B, 0xFB4F59C8, 0xC3CEDDAD]
RAW = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
MASK = 0xFFFFFFFF


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & MASK


def compress(state: list[int], block16: list[int]) -> None:
    w = block16[:]
    for i in range(16, 80):
        w.append((w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]) & MASK)
        w[i] = rol(w[i], 1)
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
    state[:] = [(state[i] + x) & MASK for i, x in enumerate([a, b, c, d, e])]


def words_from_block(data: bytes, block_endian: str) -> list[int]:
    pack = "<I" if block_endian == "le" else ">I"
    return [struct.unpack(pack, data[i : i + 4])[0] for i in range(0, 64, 4)]


def hash_variant(data: bytes, block_endian: str, length_endian: str) -> list[int]:
    state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    bitlen = len(data) * 8
    buf = bytearray(data)
    buf.append(0x80)
    while (len(buf) % 64) != 56:
        buf.append(0)
    if length_endian == "le":
        buf += struct.pack("<Q", bitlen)
    elif length_endian == "be":
        buf += struct.pack(">Q", bitlen)
    else:
        buf += struct.pack(">II", 0, bitlen)  # std: hi=0 lo=bits BE in last 8 bytes as big-endian 64-bit

    for off in range(0, len(buf), 64):
        compress(state, words_from_block(bytes(buf[off : off + 64]), block_endian))
    return state


def fmt(words: list[int]) -> str:
    return " ".join(f"{w:08X}" for w in words)


for be in ("le", "be"):
    for le in ("le", "be", "std"):
        got = hash_variant(RAW, be, le)
        if got == GUI:
            print("MATCH", be, le, fmt(got))

print("std hashlib", fmt([struct.unpack(">I", hashlib.sha1(RAW).digest()[i : i + 4])[0] for i in range(0, 20, 4)]))
print("gui", fmt(GUI))

# UTF-16 content
for enc in ("utf-16-le", "utf-16"):
    u = RAW.decode("ascii").encode(enc)
    for be in ("le", "be"):
        for le in ("le", "be", "std"):
            got = hash_variant(u, be, le)
            if got == GUI:
                print("MATCH utf", enc, be, le, fmt(got))
