#!/usr/bin/env python3
import hashlib
import struct
from pathlib import Path

data = Path(__file__).resolve().parent / "fixtures" / "digits.bin"
raw = data.read_bytes()
print("file", repr(raw))

sha = hashlib.sha1(raw).digest()
words_be = [struct.unpack(">I", sha[i : i + 4])[0] for i in range(0, 20, 4)]
print("std sha1 be", " ".join(f"{w:08X}" for w in words_be))

gui = [0x67972355, 0xBD7D1290, 0x86D9DB6B, 0xFB4F59C8, 0xC3CEDDAD]
print("gui       ", " ".join(f"{w:08X}" for w in gui))

md5 = hashlib.md5(raw).digest()
print("md5 be    ", " ".join(f"{struct.unpack('>I', md5[i:i+4])[0]:08X}" for i in range(0, 16, 4)))
