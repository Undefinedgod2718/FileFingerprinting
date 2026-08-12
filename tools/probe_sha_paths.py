#!/usr/bin/env python3
import hashlib
import struct

GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"
PATHS = [
    r"D:\Program_Coding\Q_Test\tpfilem-modern\tools\fixtures\digits.bin",
    r"D:/Program_Coding/Q_Test/tpfilem-modern/tools/fixtures/digits.bin",
    r"digits.bin",
    r"tools\fixtures\digits.bin",
    r"tools/fixtures/digits.bin",
]


def fmt(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


raw = open(__file__).replace("probe_sha_paths.py", "fixtures/digits.bin")
# fix path
from pathlib import Path

raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()

print("target", GUI)
for p in PATHS:
    for enc in ("ascii", "utf-8", "utf-16-le", "utf-16"):
        try:
            b = p.encode(enc)
        except Exception:
            continue
        s = fmt(hashlib.sha1(b).digest())
        if s == GUI:
            print("MATCH path", enc, p, s)

# path + content combos
for p in PATHS:
    pb = p.encode("ascii", errors="ignore")
    for combo in [pb + raw, raw + pb, pb + b"\x00" + raw]:
        s = fmt(hashlib.sha1(combo).digest())
        if s == GUI:
            print("MATCH combo", p)
