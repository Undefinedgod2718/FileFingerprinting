import hashlib
import struct
import binascii
import zipfile
from pathlib import Path

path = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
data = path.read_bytes()
LEGACY_SHA = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"
CHUNK = 0x2000


def fmt_sha(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


def check(label: str, payload: bytes) -> None:
    s = fmt_sha(hashlib.sha1(payload).digest())
    if s == LEGACY_SHA:
        print("*** SHA MATCH ***", label, "len", len(payload))
    print(f"{label}: {s}")


check("full", data)
check("chunk0", data[:CHUNK])
check("chunk1", data[CHUNK : 2 * CHUNK])
check("last_chunk", data[-CHUNK:])

with zipfile.ZipFile(path) as zf:
    for n in zf.namelist():
        raw = zf.read(n)
        check(f"zip_raw:{n}", raw)
        info = zf.getinfo(n)
        comp = zf.open(n).read()  # same as read for stored
        if comp != raw:
            check(f"zip_comp:{n}", comp)

# sha1 of crc32 value as 4 bytes big endian
zc = binascii.crc32(data) & 0xFFFFFFFF
for endian in ["big", "little"]:
    check(f"sha1_of_zlib_crc_{endian}", zc.to_bytes(4, endian))

# sha1 hex string of file
check("sha1_of_sha1_hex_ascii", hashlib.sha1(data).hexdigest().upper().encode())

# double sha1
check("sha1_sha1", hashlib.sha1(hashlib.sha1(data).digest()).digest())
