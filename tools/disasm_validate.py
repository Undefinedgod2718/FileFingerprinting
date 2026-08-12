#!/usr/bin/env python3
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
    lines = [f"\n=== {name} RVA=0x{rva:X} ==="]
    for insn in md.disasm(text[start : start + size], va):
        lines.append(f"0x{insn.address:08X}: {insn.mnemonic:8} {insn.op_str}")
    return lines

regions = [
    ("validate_filename_sha", 0x1C30, 0x120),
    ("sha_compute", 0x1CE0, 0x380),
    ("dialog_gen_key", 0x21F0, 0x100),
]

out = Path(__file__).parent / "ghidra_notes" / "validate_and_sha.txt"
lines: list[str] = []
for name, rva, size in regions:
    lines.extend(dump(name, rva, size))

out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out}")
