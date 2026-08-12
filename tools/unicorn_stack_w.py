#!/usr/bin/env python3
import struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32
from unicorn.x86_const import *
from unicorn_final_only import RET, STACK, STACK_SIZE, load_pe_image, EXE, IMAGE_BASE

PRE = {}


def hook(mu, address, size, user_data):
    if address == 0x00401D08:
        esp = mu.reg_read(UC_X86_REG_ESP)
        pre = struct.unpack("<6I", bytes(mu.mem_read(esp + 0xC, 24)))
        PRE["w_minus2_minus1"] = (pre[0], pre[1])
        PRE["w0_w1"] = (pre[2], pre[3])


def main() -> None:
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    load_pe_image(mu, EXE)
    mu.mem_map(STACK, STACK_SIZE)
    mu.mem_write(RET, b"\xF4")
    mu.hook_add(UC_HOOK_CODE, hook)
    ctx = STACK + STACK_SIZE - 0x2000
    buf = ctx + 0x100
    raw = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()
    mu.mem_write(ctx, b"\x00" * 0x5C)
    mu.mem_write(buf, raw)
    esp = STACK + STACK_SIZE - 0x1000
    mu.mem_write(esp, struct.pack("<II", RET, ctx))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(0x00401EF0, 0x00401F22, timeout=5_000_000)
    esp = mu.reg_read(UC_X86_REG_ESP) - 12
    mu.mem_write(esp, struct.pack("<III", RET, ctx, buf))
    mu.mem_write(esp + 12, struct.pack("<I", len(raw)))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(0x00401F30, 0x00401FC0, timeout=10_000_000)
    esp = mu.reg_read(UC_X86_REG_ESP) - 4
    mu.mem_write(esp, struct.pack("<II", RET, ctx))
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.reg_write(UC_X86_REG_ECX, IMAGE_BASE + 0x5000)
    mu.emu_start(0x00401FD0, 0x0040205A, timeout=10_000_000)
    print("stack before W[0]", PRE)


if __name__ == "__main__":
    main()
