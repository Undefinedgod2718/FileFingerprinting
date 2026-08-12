#!/usr/bin/env python3
"""Call TPFileM SHA at image base 0x400000 via VirtualAlloc."""
import ctypes
import struct
from pathlib import Path

EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
IMAGE_BASE = 0x00400000
GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"


def load_pe_at_base() -> int:
    data = EXE.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    size_image = struct.unpack_from("<I", data, pe + 24 + 56)[0]
    size = ((size_image + 0xFFF) // 0x1000) * 0x1000
    MEM_COMMIT = 0x1000
    MEM_RESERVE = 0x2000
    PAGE_EXECUTE_READWRITE = 0x40
    base = ctypes.windll.kernel32.VirtualAlloc(
        ctypes.c_void_p(IMAGE_BASE), size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE
    )
    if not base:
        raise OSError("VirtualAlloc at 0x400000 failed")
    if base != IMAGE_BASE:
        raise OSError(f"VirtualAlloc returned {base:#x}, need {IMAGE_BASE:#x}")
    opt = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
    sec = opt + struct.unpack_from("<H", data, pe + 6)[0] * 40
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    for i in range(nsec):
        off = sec + i * 40
        va, raw_size, raw_ptr = struct.unpack_from("<III", data, off + 12)[:3]
        if raw_size:
            ctypes.memmove(base + va, data[raw_ptr : raw_ptr + raw_size], raw_size)
    return base


def hash_bytes(payload: bytes) -> str:
    base = load_pe_at_base()
    init = ctypes.WINFUNCTYPE(None, ctypes.c_void_p)(base + 0x1EF0)
    update = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32)(base + 0x1F30)
    final = ctypes.WINFUNCTYPE(None, ctypes.c_void_p)(base + 0x1FD0)
    ctx = (ctypes.c_ubyte * 0x5C)()
    buf = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
    init(ctypes.byref(ctx))
    update(ctypes.byref(ctx), buf, len(payload))
  # ecx unused in final for compress path
    final(ctypes.byref(ctx))
    words = struct.unpack("<5I", bytes(ctx[:20]))
    return " ".join(f"{w:08X}" for w in words)


if __name__ == "__main__":
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    got = hash_bytes(raw)
    print(got, got == GUI)
