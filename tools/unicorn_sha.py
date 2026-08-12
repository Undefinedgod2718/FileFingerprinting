#!/usr/bin/env python3

"""Emulate TPFileM SHA at image base 0x400000 using Unicorn."""

from __future__ import annotations



import argparse

import struct

import sys

from pathlib import Path



from unicorn import Uc, UC_ARCH_X86, UC_HOOK_CODE, UC_HOOK_MEM_UNMAPPED, UC_MODE_32

from unicorn.x86_const import *



EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")

IMAGE_BASE = 0x00400000

STACK = 0x00100000

STACK_SIZE = 0x00100000





def load_pe_image(mu: Uc, path: Path) -> None:

    data = path.read_bytes()

    if data[:2] != b"MZ":

        raise ValueError("not PE")

    pe_off = struct.unpack_from("<I", data, 0x3C)[0]

    num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]

    opt_hdr = pe_off + 24

    size_image = struct.unpack_from("<I", data, opt_hdr + 56)[0]

    mu.mem_map(IMAGE_BASE, ((size_image + 0xFFF) // 0x1000) * 0x1000)

    sec = opt_hdr + struct.unpack_from("<H", data, pe_off + 20)[0]

    for _ in range(num_sections):

        name, vsize, va, raw_size, raw_ptr = struct.unpack_from("<8sIIII", data, sec)

        if raw_size:

            mu.mem_write(IMAGE_BASE + va, data[raw_ptr : raw_ptr + raw_size])

        sec += 40





def run_sha(payload: bytes) -> str:

    mu = Uc(UC_ARCH_X86, UC_MODE_32)

    load_pe_image(mu, EXE)

    mu.mem_map(STACK, STACK_SIZE)



    ctx_addr = STACK + STACK_SIZE - 0x2000

    buf_addr = ctx_addr + 0x100

    mu.mem_write(ctx_addr, b"\x00" * 0x5C)

    mu.mem_write(buf_addr, payload)



    ret_stub = STACK + STACK_SIZE - 0x80

    mu.mem_write(ret_stub, b"\xF4")  # hlt



    def hook_mem(uc, access, address, size, value, user_data):

        raise RuntimeError(f"unmapped mem {access:#x} @ {address:#x}")



    def hook_code(uc, address, size, user_data):

        if address in (0x004171E4, 0x00417144, 0x00417148):

            raise RuntimeError("external API hit")



    mu.hook_add(UC_HOOK_MEM_UNMAPPED, hook_mem)

    mu.hook_add(UC_HOOK_CODE, hook_code)



    esp = STACK + STACK_SIZE - 0x1000

    mu.mem_write(esp, struct.pack("<II", ret_stub, ctx_addr))

    mu.reg_write(UC_X86_REG_ESP, esp)

    mu.reg_write(UC_X86_REG_EIP, 0x00401EF0)

    mu.emu_start(0x00401EF0, 0x00401F22, timeout=5_000_000)



    esp = mu.reg_read(UC_X86_REG_ESP)

    esp -= 12

    mu.mem_write(esp, struct.pack("<III", ret_stub, ctx_addr, buf_addr))

    mu.mem_write(esp + 12, struct.pack("<I", len(payload)))

    mu.reg_write(UC_X86_REG_ESP, esp)

    mu.reg_write(UC_X86_REG_EIP, 0x00401F30)

    mu.emu_start(0x00401F30, 0x00401FC0, timeout=10_000_000)



    esp = mu.reg_read(UC_X86_REG_ESP)

    esp -= 4

    mu.mem_write(esp, struct.pack("<II", ret_stub, ctx_addr))

    mu.reg_write(UC_X86_REG_ESP, esp)

    mu.reg_write(UC_X86_REG_ECX, IMAGE_BASE + 0x5000)

    mu.reg_write(UC_X86_REG_EIP, 0x00401FD0)

    mu.emu_start(0x00401FD0, 0x0040205A, timeout=10_000_000)



    raw = bytes(mu.mem_read(ctx_addr, 20))

    words = struct.unpack("<5I", raw)

    return " ".join(f"{w:08X}" for w in words)





def main() -> int:

    parser = argparse.ArgumentParser(description="TPFileM legacy SHA via Unicorn")

    parser.add_argument("--stdin", action="store_true", help="read u32 LE length + bytes from stdin")

    parser.add_argument("--file", type=Path, help="hash file contents")

    parser.add_argument("--self-test", action="store_true", help="verify digits.bin golden")

    args = parser.parse_args()



    if args.self_test:

        data = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()

        got = run_sha(data)

        gui = "67972355 BD7D1290 86D9DB6B FB4F59C8 C3CEDDAD"

        print("match", got == gui)

        return 0 if got == gui else 1



    if args.stdin:

        hdr = sys.stdin.buffer.read(4)

        if len(hdr) != 4:

            print("stdin length header required", file=sys.stderr)

            return 2

        (n,) = struct.unpack("<I", hdr)

        data = sys.stdin.buffer.read(n) if n else b""

        if len(data) != n:

            print("short stdin payload", file=sys.stderr)

            return 2

    elif args.file is not None:

        data = args.file.read_bytes()

    else:

        data = (Path(__file__).resolve().parent / "fixtures" / "digits.bin").read_bytes()



    print(run_sha(data))

    return 0





if __name__ == "__main__":

    raise SystemExit(main())

