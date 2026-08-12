#!/usr/bin/env python3
import hashlib
import struct
from pathlib import Path

RAW = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"


def fmt_be(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, len(d), 4))


def fmt_words(words: list[int]) -> str:
    return " ".join(f"{w:08X}" for w in words)


print("target", GUI)
for name in sorted(hashlib.algorithms_available):
    if name in {"shake_128", "shake_256"}:
        continue
    try:
        h = hashlib.new(name, RAW).digest()
    except Exception:
        continue
    if len(h) < 20:
        continue
    be = fmt_be(h[:20])
    if be == GUI:
        print("MATCH", name, be)
    le = fmt_words([struct.unpack("<I", h[i : i + 4])[0] for i in range(0, 20, 4)])
    if le == GUI:
        print("MATCH le", name, le)

# nibble / word permutations on std sha1
d = hashlib.sha1(RAW).digest()
words = [struct.unpack(">I", d[i : i + 4])[0] for i in range(0, 20, 4)]
for perm in [
    words,
    words[::-1],
    [int(f"{w:08X}"[::-1], 16) for w in words],
]:
    s = fmt_words(perm)
    if s == GUI:
        print("perm match", s)
