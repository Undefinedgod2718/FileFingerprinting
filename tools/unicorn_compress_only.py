#!/usr/bin/env python3
"""Single sha1_compress call via Unicorn — isolate algorithm."""
import struct
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import *
from unicorn_sha import EXE, STACK, STACK_SIZE, load_pe_image, IMAGE_BASE

RET = STACK + STACK_SIZE - 0x80
BLOCK_HEX = (
    "313233343536373839800000000000000000000000000000000000000000000000"
    "00000000000000000000000000000000000000000000000000000000000048000000"
)


def run_compress() -> str:
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    load_pe_image(mu, EXE)
    mu.mem_map(STACK, STACK_SIZE)
    mu.mem_write(RET, b"\xF4")
    ctx = STACK + STACK_SIZE - 0x2000
    mu.mem_write(ctx, b"\x00" * 0x5C)
    struct.pack_into("<5I", (buf := bytearray(20)), 0, 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)
    mu.mem_write(ctx, bytes(buf))
    mu.mem_write(ctx + 0x1C, bytes.fromhex(BLOCK_HEX))
    esp = STACK + STACK_SIZE - 0x1000
    mu.mem_write(esp, struct.pack("<II", RET, ctx))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.reg_write(UC_X86_REG_ECX, IMAGE_BASE + 0x5000)
    mu.emu_start(0x00401CE0, 0x00401EEB, timeout=10_000_000)
    words = struct.unpack("<5I", bytes(mu.mem_read(ctx, 20)))
    return " ".join(f"{w:08X}" for w in words)


print(run_compress())
print("67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD")
