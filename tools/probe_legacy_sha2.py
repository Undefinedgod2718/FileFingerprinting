import hashlib
import struct
import zipfile
from pathlib import Path

path = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
LEGACY_SHA = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"
data = path.read_bytes()


def fmt_sha(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


def try_payload(label: str, payload: bytes) -> None:
    s = fmt_sha(hashlib.sha1(payload).digest())
    if s == LEGACY_SHA:
        print("*** MATCH ***", label)


# compressed payloads from zip structure
with open(path, "rb") as f:
    raw = f.read()

with zipfile.ZipFile(path) as zf:
    for info in zf.infolist():
        start = info.header_offset + 30 + len(info.filename) + len(info.extra)
        if info.flag_bits & 0x8:
            continue
        comp = raw[start : start + info.compress_size]
        try_payload(f"compressed:{info.filename}", comp)
        try_payload(f"stored_read:{info.filename}", zf.read(info.filename))

# path variants
for p in [
    str(path),
    str(path).replace("\\", "/"),
    path.name,
    r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx",
]:
    try_payload("path:" + p, p.encode("utf-8"))
    try_payload("path_mbcs:" + p, p.encode("mbcs", errors="ignore"))

# maybe sha is NOT sha1 - try sha256 first 20 bytes formatted
d256 = hashlib.sha256(data).digest()
try_payload("sha256_first20", d256[:20])

# md5 + first 4 bytes of md5 as 5th word? weird

# brute: sha1 with initial state wrong?

print("done, no match unless printed above")
