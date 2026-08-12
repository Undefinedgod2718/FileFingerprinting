import hashlib
import struct
from pathlib import Path

data = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx").read_bytes()
LEGACY = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"


def fmt(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


for n in range(max(0, len(data) - 5000), len(data) + 1):
    s = fmt(hashlib.sha1(data[:n]).digest())
    if s == LEGACY:
        print("MATCH length", n)
        break
else:
    print("no length match in last 5000 bytes")

# image only range approx - find PNG signature
idx = data.find(b"\x89PNG")
print("png offset", idx)
if idx >= 0:
  # find IEND
  end = data.find(b"IEND", idx) + 8
  print("png end", end, "sha", fmt(hashlib.sha1(data[idx:end]).digest()))

print("legacy", LEGACY)
