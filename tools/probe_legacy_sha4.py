import hashlib
import struct
from pathlib import Path

path = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
LEGACY_CRC = "A25E39C9"
LEGACY_SHA = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"


def fmt_sha(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


def check(label, payload: bytes):
    s = fmt_sha(hashlib.sha1(payload).digest())
    if s == LEGACY_SHA:
        print("MATCH", label, repr(payload[:80]))


parts = [
    LEGACY_CRC.encode(),
    LEGACY_CRC.lower().encode(),
    path.name.encode(),
    str(path).encode(),
    b"A25E39C9" + path.name.encode(),
    path.name.encode() + b"A25E39C9",
    LEGACY_CRC.encode() + str(path).encode(),
]

for p in parts:
    check("solo", p)

data = path.read_bytes()
for p in parts:
    check("concat_file", p + data)
    check("file_concat", data + p)

# custom tp sha? use openssl - no

# maybe display is NOT sha1 but second crc-like rolling hash
# try md5 formatted as 4+1 words
md = hashlib.md5(data).digest()
print("md5_words", fmt_sha(md + md[:4]))

# sha1 of file with legacy crc appended as binary
check("file+crc_be", data + bytes.fromhex(LEGACY_CRC))
check("crc_be+file", bytes.fromhex(LEGACY_CRC) + data)

print("done")
