#!/usr/bin/env python3
"""Disassemble key regions of legacy TPFileM.exe for RE notes."""
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from pathlib import Path

EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
IMAGE_BASE = 0x00400000
TEXT_OFF = 0x1000
TEXT_VA = IMAGE_BASE + 0x1000

data = EXE.read_bytes()
text = data[TEXT_OFF:TEXT_OFF + 0x16000]

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

regions = [
    ("crc_poly_ref", 0x17C1 - 0x80, 0x200),
    ("crc_string_xref_1", 0x19E6 - 0x80, 0x200),
    ("crc_string_xref_2", 0x1AC9 - 0x80, 0x200),
    ("entry_adjacent", 0x1A50, 0x300),
]

out = Path(__file__).parent / "ghidra_notes" / "disasm_regions.txt"
out.parent.mkdir(parents=True, exist_ok=True)

lines = []
for name, start, size in regions:
    chunk = text[start : start + size]
    va = TEXT_VA + start
    lines.append(f"\n=== {name} @ RVA 0x{start + 0x1000:X} ===")
    for insn in md.disasm(chunk, va):
        lines.append(f"0x{insn.address:08X}: {insn.mnemonic:8} {insn.op_str}")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out}")
