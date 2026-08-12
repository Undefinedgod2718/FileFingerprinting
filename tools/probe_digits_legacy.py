import binascii
import hashlib
import struct

data = b"123456789"
LEGACY_CRC = "CBF43926"
LEGACY_SHA = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"


def fmt_sha(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


def fmt_sha_le(d: bytes) -> str:
    return " ".join(f"{int.from_bytes(d[i : i + 4], 'little'):08X}" for i in range(0, 20, 4))


print("legacy_crc", LEGACY_CRC, "zlib", f"{binascii.crc32(data) & 0xFFFFFFFF:08X}")
print("legacy_sha", LEGACY_SHA)
print("sha1_be", fmt_sha(hashlib.sha1(data).digest()))
print("sha1_le", fmt_sha_le(hashlib.sha1(data).digest()))
print("md5_be", fmt_sha(hashlib.md5(data).digest()))
print("sha256_first20_be", fmt_sha(hashlib.sha256(data).digest()[:20]))
