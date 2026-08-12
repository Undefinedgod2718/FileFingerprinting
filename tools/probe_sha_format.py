import hashlib
import struct
import binascii
from pathlib import Path

p = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
data = p.read_bytes()
d = hashlib.sha1(data).digest()
legacy_sha = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"

words_be = " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))
words_le = " ".join(f"{int.from_bytes(d[i : i + 4], 'little'):08X}" for i in range(0, 20, 4))

print("sha1_hex", d.hex().upper())
print("sha1_words_be", words_be)
print("sha1_words_le", words_le)
print("legacy_sha", legacy_sha)
print("match_be", words_be == legacy_sha)
print("match_le", words_le == legacy_sha)
print("zlib_crc", f"{binascii.crc32(data) & 0xFFFFFFFF:08X}")

# digits test vector
for payload in [b"123456789", b"test", b""]:
    tp = None
    # quick tp crc from known
    POLY = 0x04C11DB7
    t = []
    for i in range(256):
        crc = i << 24
        for _ in range(8):
            crc = ((crc << 1) ^ POLY) if crc & 0x80000000 else (crc << 1)
            crc &= 0xFFFFFFFF
        t.append(crc)
    c = 0xFFFFFFFF
    for b in payload:
        c = ((c >> 8) ^ t[(c ^ b) & 0xFF]) & 0xFFFFFFFF
    tp_crc = (~c) & 0xFFFFFFFF
    z = binascii.crc32(payload) & 0xFFFFFFFF
    print(repr(payload), "tp", f"{tp_crc:08X}", "zlib", f"{z:08X}")
