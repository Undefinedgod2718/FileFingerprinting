import binascii
import hashlib
import struct
from pathlib import Path

fixtures = Path(__file__).resolve().parent / "fixtures"
for name in ["empty.bin", "digits.bin", "test.bin", "seq16.bin"]:
    p = fixtures / name
    if not p.exists():
        continue
    data = p.read_bytes()
    POLY = 0x04C11DB7
    t = []
    for i in range(256):
        crc = i << 24
        for _ in range(8):
            crc = ((crc << 1) ^ POLY) if crc & 0x80000000 else (crc << 1)
            crc &= 0xFFFFFFFF
        t.append(crc)
    c = 0xFFFFFFFF
    for b in data:
        c = ((c >> 8) ^ t[(c ^ b) & 0xFF]) & 0xFFFFFFFF
    tp = (~c) & 0xFFFFFFFF
    z = binascii.crc32(data) & 0xFFFFFFFF
    sha = " ".join(f"{struct.unpack('>I', hashlib.sha1(data).digest()[i:i+4])[0]:08X}" for i in range(0, 20, 4))
    print(name, "tp_crc", f"{tp:08X}", "zlib_crc", f"{z:08X}", "sha", sha)

docx = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
data = docx.read_bytes()
print("--- docx ---")
print("tp_crc", f"{tp:08X}" if False else "")
# recompute
c = 0xFFFFFFFF
for b in data:
    c = ((c >> 8) ^ t[(c ^ b) & 0xFF]) & 0xFFFFFFFF
tp = (~c) & 0xFFFFFFFF
z = binascii.crc32(data) & 0xFFFFFFFF
sha = " ".join(f"{struct.unpack('>I', hashlib.sha1(data).digest()[i:i+4])[0]:08X}" for i in range(0, 20, 4))
print("docx tp_crc", f"{tp:08X}", "zlib_crc", f"{z:08X}", "sha", sha)
print("legacy_crc A25E39C9 legacy_sha BB741E73 A3136085 49B3225A C5F9B80B E0287945")
