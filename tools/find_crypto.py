#!/usr/bin/env python3
"""Find and disassemble CRC/SHA candidate functions in TPFileM.exe."""
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from pathlib import Path
import struct

EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
IMAGE_BASE = 0x00400000
data = EXE.read_bytes()

def rva_to_offset(rva: int) -> int:
    # single-section mapping for .text/.rdata with same raw=va offset pattern
    if 0x1000 <= rva < 0x23000:
        return rva
    return rva

def read_cstring(file_off: int) -> str:
    end = data.find(b"\x00", file_off)
    return data[file_off:end].decode("ascii", errors="replace")

# Find all push imm32 pointing into .data/.rdata (0x0041xxxx)
md = Cs(CS_ARCH_X86, CS_MODE_32)
text = data[0x1000:0x17000]
hits = []
for i in range(len(text) - 5):
    if text[i] == 0x68:  # push imm32
        imm = struct.unpack_from("<I", text, i + 1)[0]
        if 0x00417000 <= imm <= 0x00422000:
            s = read_cstring(imm - IMAGE_BASE)
            if any(k in s for k in ("CRC", "SHA", "Error", "Key", "Step", "%08X")):
                hits.append((0x1000 + i, imm, s[:60]))

out = Path(__file__).parent / "ghidra_notes" / "string_push_sites.txt"
lines = ["push sites referencing key strings:"]
for file_off, imm, s in hits:
    va = IMAGE_BASE + file_off
    lines.append(f"  file=0x{file_off:X} va=0x{va:X} -> 0x{imm:X} \"{s}\"")

# Disassemble around CRC loop - search for 0xFFFFFFFF xor pattern in tight loops
lines.append("\n=== Functions with 0xEDB88320 or bit-test loops near poly ===")
poly_ref = text.find(struct.pack("<I", 0x04C11DB7))
if poly_ref >= 0:
    start = max(0, poly_ref - 0x100)
    va = IMAGE_BASE + 0x1000 + start
    for insn in md.disasm(text[start:poly_ref+0x180], va):
        lines.append(f"0x{insn.address:08X}: {insn.mnemonic:8} {insn.op_str}")

# Search SHA1 init constants (0x67452301)
sha_const = struct.pack("<I", 0x67452301)
pos = 0
lines.append("\n=== SHA1 constant 0x67452301 sites ===")
while True:
    idx = data.find(sha_const, pos)
    if idx < 0:
        break
    lines.append(f"  offset 0x{idx:X}")
    pos = idx + 1

out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out}, {len(hits)} string push hits")
