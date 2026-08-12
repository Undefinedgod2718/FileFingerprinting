import hashlib
import struct
import subprocess
import json
from pathlib import Path

POLY = 0x04C11DB7
FILE_PATH = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
MCP = Path(r"D:\Program_Coding\Q_Test\tpfilem-modern\publish\app\TpFileM.Mcp.exe")

def build_table():
    t = []
    for i in range(256):
        crc = i << 24
        for _ in range(8):
            crc = ((crc << 1) ^ POLY) if crc & 0x80000000 else (crc << 1)
            crc &= 0xFFFFFFFF
        t.append(crc)
    return t

TABLE = build_table()

def crc32_tp(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for b in data:
        crc = ((crc >> 8) ^ TABLE[(crc ^ b) & 0xFF]) & 0xFFFFFFFF
    return (~crc) & 0xFFFFFFFF

def fmt_sha(d: bytes) -> str:
    words = [struct.unpack(">I", d[i : i + 4])[0] for i in range(0, 20, 4)]
    return " ".join(f"{w:08X}" for w in words)

data = FILE_PATH.read_bytes()
print("FILE", FILE_PATH)
print("SIZE", len(data))
print("MODERN_CRC", f"{crc32_tp(data):08X}")
print("MODERN_SHA", fmt_sha(hashlib.sha1(data).digest()))

if MCP.exists():
    req = "\n".join([
        '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}',
        json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "generate_key",
                "arguments": {"file_path": str(FILE_PATH)},
            },
        }),
    ])
    p = subprocess.run([str(MCP)], input=req, capture_output=True, text=True, timeout=15)
    for line in p.stdout.splitlines():
        if '"crc_key"' in line or '"sha_key"' in line:
            print("MCP_LINE", line.strip())
