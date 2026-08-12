import hashlib
import re
import struct
import zipfile
from pathlib import Path

path = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")
LEGACY = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"


def fmt(d: bytes) -> str:
    return " ".join(f"{struct.unpack('>I', d[i : i + 4])[0]:08X}" for i in range(0, 20, 4))


with zipfile.ZipFile(path) as z:
    xml = z.read("word/document.xml").decode("utf-8")

text = re.sub(r"<[^>]+>", "", xml)
for label, payload in [
    ("xml", xml.encode()),
    ("text", text.encode()),
    ("text_utf16", text.encode("utf-16le")),
]:
    s = fmt(hashlib.sha1(payload).digest())
    print(label, s, "MATCH" if s == LEGACY else "")

try:
    from docx import Document

    doc = Document(path)
    plain = "\n".join(p.text for p in doc.paragraphs)
    s = fmt(hashlib.sha1(plain.encode()).digest())
    print("docx_paragraphs", s, "MATCH" if s == LEGACY else "")
except Exception as e:
    print("docx err", e)
