#!/usr/bin/env python3
import binascii
import hashlib
import struct
import zipfile
from pathlib import Path

POLY = 0x04C11DB7
path = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
data = path.read_bytes()
LEGACY_CRC = 0xA25E39C9
LEGACY_SHA = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"


def build_table():
    t = []
    for i in range(256):
        crc = i << 24
        for _ in range(8):
            crc = ((crc << 1) ^ POLY) if crc & 0x80000000 else (crc << 1)
            crc &= 0xFFFFFFFF
        t.append(crc)
    return t


TABLE = build_table()


def crc_tp(b: bytes) -> int:
    crc = 0xFFFFFFFF
    for x in b:
        crc = ((crc >> 8) ^ TABLE[(crc ^ x) & 0xFF]) & 0xFFFFFFFF
    return (~crc) & 0xFFFFFFFF


def fmt_sha(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


def report(label: str, payload: bytes) -> None:
    c = crc_tp(payload)
    s = fmt_sha(hashlib.sha1(payload).digest())
    mark = []
    if c == LEGACY_CRC:
        mark.append("CRC_MATCH")
    if s == LEGACY_SHA:
        mark.append("SHA_MATCH")
    if mark:
        print(f"*** {' '.join(mark)} *** {label} len={len(payload)}")
    print(f"{label}: crc={c:08X} sha={s}")


print("LEGACY", f"crc={LEGACY_CRC:08X}", f"sha={LEGACY_SHA}")
print("zlib", f"{binascii.crc32(data) & 0xFFFFFFFF:08X}")
report("full_file", data)

with zipfile.ZipFile(path) as zf:
    combined = b"".join(zf.read(n) for n in sorted(zf.namelist()))
    report("zip_all_uncompressed_concat", combined)
    for name in zf.namelist():
        report(f"zip:{name}", zf.read(name))

for label, payload in [
    ("minus1", data[:-1]),
    ("from512", data[512:]),
    ("crlf_norm", data.replace(b"\r\n", b"\n")),
]:
    report(label, payload)
