#!/usr/bin/env python3
"""Compare GUI zlib CRC vs Ghidra RE custom CRC (0x04C11DB7)."""
from pathlib import Path
import struct
import binascii

# --- gui_zlib: what Delta TPFileM GUI displays (authoritative) ---
def crc32_zlib(data_bytes: bytes) -> int:
    return binascii.crc32(data_bytes) & 0xFFFFFFFF

# --- re_custom: Ghidra path @ 0x4019C0 (NOT wired to GUI CRC field) ---
POLY = 0x04C11DB7
data = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe").read_bytes()

def transform_4017f0(value: int, count: int) -> int:
    """Emulate sub_4017F0: extract `count` low bits from value into a bitmask."""
    value &= 0xFFFFFFFF
    if count + 1 <= 1:
        return 0
    result = 0
    v = value
    for _ in range(count):
        if v & 1:
            result |= 1 << _
        v >>= 1
    return result & 0xFFFFFFFF

def build_table() -> list[int]:
    table = []
    for i in range(256):
        crc = (i << 24) & 0xFFFFFFFF
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) & 0xFFFFFFFF) ^ POLY
            else:
                crc = (crc << 1) & 0xFFFFFFFF
        crc = transform_4017f0(crc, 0x20)
        table.append(crc)
    return table

TABLE = build_table()

def crc32_tp(data_bytes: bytes) -> int:
    crc = 0xFFFFFFFF
    for b in data_bytes:
        idx = (crc ^ b) & 0xFF
        crc = ((crc >> 8) ^ TABLE[idx]) & 0xFFFFFFFF
    return (~crc) & 0xFFFFFFFF

# gui_zlib vs re_custom
print("=== gui_zlib vs re_custom ===")
for payload in [b"", b"123456789", bytes(range(16)), b"test"]:
    print(
        f"{payload!r}: gui_zlib={crc32_zlib(payload):08X} "
        f"re_custom={crc32_tp(payload):08X}"
    )

# Legacy RE table dump (optional)
data = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe").read_bytes()
def build_raw():
    t = []
    for i in range(256):
        crc = (i << 24) & 0xFFFFFFFF
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) & 0xFFFFFFFF) ^ POLY
            else:
                crc = (crc << 1) & 0xFFFFFFFF
        t.append(crc)
    return t

RAW = build_raw()

def crc_raw(data_bytes: bytes) -> int:
    crc = 0xFFFFFFFF
    for b in data_bytes:
        idx = (crc ^ b) & 0xFF
        crc = ((crc >> 8) ^ RAW[idx]) & 0xFFFFFFFF
    return (~crc) & 0xFFFFFFFF

print("--- raw table ---")
for payload in [b"123456789", b"test"]:
    print(f"{payload!r}: raw={crc_raw(payload):08X}")

# reflected poly table (standard)
def build_std_reflected():
    poly = 0xEDB88320
    t = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
        t.append(crc)
    return t

STD = build_std_reflected()

def crc_std(data_bytes: bytes) -> int:
    crc = 0xFFFFFFFF
    for b in data_bytes:
        crc = STD[(crc ^ b) & 0xFF] ^ (crc >> 8)
        crc &= 0xFFFFFFFF
    return crc ^ 0xFFFFFFFF

print("--- std reflected ---")
for payload in [b"123456789", b"test"]:
    print(f"{payload!r}: std={crc_std(payload):08X}")
