#!/usr/bin/env python3
"""Call TPFileM.exe SHA routines in-process via ctypes (image base 0x400000)."""
from __future__ import annotations

import ctypes
import struct
from pathlib import Path

EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
GUI = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"
IMAGE_BASE = 0x00400000

# RVAs
RVA_SHA_INIT = 0x401EF0 - IMAGE_BASE
RVA_SHA_UPDATE = 0x401F30 - IMAGE_BASE
RVA_SHA_FINAL = 0x401FD0 - IMAGE_BASE


class TPFileMShaProbe:
    def __init__(self) -> None:
        self.data = EXE.read_bytes()
        # ponytail: single .text mapping — good enough for RVAs 0x1000..0x17000
        self.size = 0x23000
        self.mem = ctypes.create_string_buffer(self.data[: self.size], self.size)
        self.base = ctypes.addressof(self.mem)
        # VirtualProtect to RX — buffer may already be RWX in CPython alloc
        PAGE_EXECUTE_READWRITE = 0x40
        ctypes.windll.kernel32.VirtualProtect(
            ctypes.c_void_p(self.base), self.size, PAGE_EXECUTE_READWRITE, ctypes.byref(ctypes.c_ulong())
        )
        self._init = ctypes.WINFUNCTYPE(None, ctypes.c_void_p)(self.base + RVA_SHA_INIT)
        self._update = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32)(
            self.base + RVA_SHA_UPDATE
        )
        self._final = ctypes.WINFUNCTYPE(None, ctypes.c_void_p)(self.base + RVA_SHA_FINAL)

    def hash_bytes(self, payload: bytes) -> str:
        ctx = (ctypes.c_ubyte * 0x5C)()
        self._init(ctypes.byref(ctx))
        buf = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
        # FUN_00401f30 is stdcall: ctx, data, len — but disasm shows ecx=dialog unused
        self._update(ctypes.byref(ctx), buf, len(payload))
        self._final(ctypes.byref(ctx))
        words = struct.unpack("<5I", bytes(ctx[:20]))
        return " ".join(f"{w:08X}" for w in words)


def main() -> None:
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    probe = TPFileMShaProbe()
    got = probe.hash_bytes(raw)
    print("native call", got)
    print("gui       ", GUI)
    print("match", got == GUI)


if __name__ == "__main__":
    main()
