import hashlib
import re
import struct
import zipfile
from pathlib import Path

p = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
LEGACY = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"


def fmt(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


with zipfile.ZipFile(p) as z:
    xml = z.read("word/document.xml").decode()

nodes = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)
all_text = "".join(nodes)
print("nodes", [repr(n) for n in nodes])
print("all_text", repr(all_text))
for label, payload in [("all_text", all_text.encode()), ("nodes_join_nl", "\n".join(nodes).encode())]:
    s = fmt(hashlib.sha1(payload).digest())
    print(label, s, "MATCH" if s == LEGACY else "")
