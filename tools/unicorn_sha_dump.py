#!/usr/bin/env python3
import struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import *
from unicorn_sha import EXE, IMAGE_BASE, STACK, STACK_SIZE, load_pe_image

RET_STUB = STACK + STACK_SIZE - 0x80


def run_full(payload: bytes) -> tuple[bytes, str]:
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    load_pe_image(mu, EXE)
    mu.mem_map(STACK, STACK_SIZE)
    mu.mem_write(RET_STUB, b"\xF4")
    ctx_addr = STACK + STACK_SIZE - 0x2000
    buf_addr = ctx_addr + 0x100
    mu.mem_write(ctx_addr, b"\x00" * 0x5C)
    mu.mem_write(buf_addr, payload)
    esp = STACK + STACK_SIZE - 0x1000
    mu.mem_write(esp, struct.pack("<II", RET_STUB, ctx_addr))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(0x00401EF0, 0x00401F22, timeout=5_000_000)
    esp = mu.reg_read(UC_X86_REG_ESP) - 12
    mu.mem_write(esp, struct.pack("<III", RET_STUB, ctx_addr, buf_addr))
    mu.mem_write(esp + 12, struct.pack("<I", len(payload)))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(0x00401F30, 0x00401FC0, timeout=10_000_000)
    esp = mu.reg_read(UC_X86_REG_ESP) - 4
    mu.mem_write(esp, struct.pack("<II", RET_STUB, ctx_addr))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.reg_write(UC_X86_REG_ECX, IMAGE_BASE + 0x5000)
    mu.emu_start(0x00401FD0, 0x0040205A, timeout=10_000_000)
    block = bytes(mu.mem_read(ctx_addr + 0x1C, 64))
    words = struct.unpack("<5I", bytes(mu.mem_read(ctx_addr, 20)))
    return block, " ".join(f"{w:08X}" for w in words)


if __name__ == "__main__":
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    block, sha = run_full(raw)
    print("final block", block.hex())
    print("sha", sha)
