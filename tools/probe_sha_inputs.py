#!/usr/bin/env python3
"""Brute common inputs to match legacy GUI SHA for digits.bin."""
import hashlib
import struct
from pathlib import Path

GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "digits.bin"
PATH = r"D:\Program_Coding\Q_Test\tpfilem-modern\tools\fixtures\digits.bin"
raw = FIXTURE.read_bytes()


def fmt_be(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, len(d) - len(d) % 4, 4))


def fmt_state(words: list[int]) -> str:
    return " ".join(f"{w & 0xFFFFFFFF:08X}" for w in words)


def sha1_words(data: bytes) -> str:
    return fmt_be(hashlib.sha1(data).digest())


candidates = {
    "file_bytes": raw,
    "file_nul": raw + b"\x00",
    "ascii_path": PATH.encode("ascii"),
    "ascii_path_lower": PATH.lower().encode("ascii"),
    "basename": b"digits.bin",
    "crc_key": b"CBF43926",
    "crc_key_lower": b"cbf43926",
    "digits_str": b"123456789",
}

print("target", GUI)
for name, data in candidates.items():
    got = sha1_words(data)
    mark = " <-- MATCH" if got == GUI else ""
    print(f"{name:20} {got}{mark}")

# LE word format from digest
d = hashlib.sha1(raw).digest()
le = " ".join(f"{int.from_bytes(d[i:i+4],'little'):08X}" for i in range(0, 20, 4))
print(f"{'sha1_le_words':20} {le}")
