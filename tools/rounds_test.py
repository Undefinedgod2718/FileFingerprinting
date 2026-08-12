#!/usr/bin/env python3
"""Capture unicorn W and test rounds in one process."""
import struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32
from unicorn.x86_const import *
from unicorn_sha import EXE, STACK, STACK_SIZE, load_pe_image, IMAGE_BASE

MASK = 0xFFFFFFFF
RET = STACK + STACK_SIZE - 0x80
W = []


def hook(mu, address, size, user_data):
    if address == 0x00401D22:
        esp = mu.reg_read(UC_X86_REG_ESP)
        W[:] = list(struct.unpack("<80I", bytes(mu.mem_read(esp + 0x14, 320))))


def run_unicorn(payload: bytes) -> None:
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    load_pe_image(mu, EXE)
    mu.mem_map(STACK, STACK_SIZE)
    mu.mem_write(RET, b"\xF4")
    mu.hook_add(UC_HOOK_CODE, hook)
    ctx = STACK + STACK_SIZE - 0x2000
    buf = ctx + 0x100
    mu.mem_write(ctx, b"\x00" * 0x5C)
    mu.mem_write(buf, payload)
    esp = STACK + STACK_SIZE - 0x1000
    mu.mem_write(esp, struct.pack("<II", RET, ctx))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(0x00401EF0, 0x00401F22, timeout=5_000_000)
    esp = mu.reg_read(UC_X86_REG_ESP) - 12
    mu.mem_write(esp, struct.pack("<III", RET, ctx, buf))
    mu.mem_write(esp + 12, struct.pack("<I", len(payload)))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(0x00401F30, 0x00401FC0, timeout=10_000_000)
    esp = mu.reg_read(UC_X86_REG_ESP) - 4
    mu.mem_write(esp, struct.pack("<II", RET, ctx))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.reg_write(UC_X86_REG_ECX, IMAGE_BASE + 0x5000)
    mu.emu_start(0x00401FD0, 0x0040205A, timeout=10_000_000)


def rounds(w):
    def rol(x, n):
        return ((x & MASK) << n | (x & MASK) >> (32 - n)) & MASK

    state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    a, b, c, d, e = state
    for i in range(80):
        if i < 20:
            f, k = (b & c) | (~b & d), 0x5A827999
        elif i < 40:
            f, k = b ^ c ^ d, 0x6ED9EBA1
        elif i < 60:
            f, k = (b & c) | (b & d) | (c & d), 0x8F1BBCDC
        else:
            f, k = b ^ c ^ d, 0xCA62C1D6
        temp = (rol(a, 5) + f + e + k + w[i]) & MASK
        e, d, c, b, a = d, c, rol(b, 30), a, temp
    return [(state[i] + v) & MASK for i, v in enumerate([a, b, c, d, e])]


if __name__ == "__main__":
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    run_unicorn(raw)
    got = rounds(W)
    gui = [0x67972355, 0xBD7D1290, 0x86D9DB6B, 0xFB4F59C8, 0xC3CEDDAD]
    print("rounds", " ".join(f"{x:08X}" for x in got))
    print("match", got == gui)
