#!/usr/bin/env python3
"""Disassemble by PE RVA (offset from image base 0x400000)."""
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from pathlib import Path

IMAGE_BASE = 0x00400000
TEXT_RVA = 0x1000
data = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe").read_bytes()
text = data[TEXT_RVA : TEXT_RVA + 0x16000]
md = Cs(CS_ARCH_X86, CS_MODE_32)

def dump(name: str, rva: int, size: int = 0x200) -> list[str]:
    start = rva - TEXT_RVA
    va = IMAGE_BASE + rva
    lines = [f"\n=== {name} RVA=0x{rva:X} VA=0x{va:X} ==="]
    for insn in md.disasm(text[start : start + size], va):
        lines.append(f"0x{insn.address:08X}: {insn.mnemonic:8} {insn.op_str}")
    return lines

regions = [
    ("crc_table_build", 0x1790, 0x70),
    ("crc_byte_loop", 0x17F0, 0x40),
    ("gen_key_crc", 0x19B0, 0x180),
    ("gen_key_sha", 0x2040, 0x220),
    ("filename_validate", 0x1C40, 0x120),
    ("filename_sha_fail", 0x2220, 0x80),
    ("dialog_main", 0x13A0, 0x200),
]

out = Path(__file__).parent / "ghidra_notes" / "key_functions.txt"
lines: list[str] = []
for name, rva, size in regions:
    lines.extend(dump(name, rva, size))

out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out}")
