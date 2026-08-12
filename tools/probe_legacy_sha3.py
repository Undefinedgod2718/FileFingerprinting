import hashlib
import struct
from pathlib import Path

path = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
data = path.read_bytes()
LEGACY_SHA = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"


def fmt_sha(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


def check(label, payload):
    s = fmt_sha(hashlib.sha1(payload).digest())
    if s == LEGACY_SHA:
        print("MATCH", label)


def swap32(b: bytes) -> bytes:
    out = bytearray()
    for i in range(0, len(b) - len(b) % 4, 4):
        out.extend(b[i : i + 4][::-1])
    out.extend(b[len(b) - len(b) % 4 :])
    return bytes(out)


check("swap32", swap32(data))
check("reverse_all", data[::-1])
check("xor_ff", bytes(x ^ 0xFF for x in data))

# utf16le decode re-encode
try:
    check("utf16le_roundtrip", data.decode("utf-16le").encode("utf-16le"))
except Exception:
    pass

# every other byte
check("even_bytes", data[0::2])
check("odd_bytes", data[1::2])

# without zip local headers - from byte 0x4E?
for skip in [0x4E, 0x30, 0x200, 0x400, 0x2000]:
    check(f"skip_{skip}", data[skip:])

print("legacy", LEGACY_SHA)
print("standard", fmt_sha(hashlib.sha1(data).digest()))
