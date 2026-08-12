#!/usr/bin/env python3
"""Compare unicorn oracle vs TpFileM.LegacySha.Cli native helper."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from unicorn_sha import run_sha

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "src/TpFileM.LegacySha.Cli/bin/Release/net10.0/win-x86/publish/TpFileM.LegacySha.Cli.exe"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def native_sha(path: Path) -> str:
    proc = subprocess.run(
        [str(CLI), "--file", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def main() -> int:
    if not CLI.exists():
        print(f"missing {CLI}", file=sys.stderr)
        return 2

    cases = ["empty.bin", "digits.bin", "test.bin", "seq16.bin"]
    ok = True
    for name in cases:
        path = FIXTURES / name
        uni = run_sha(path.read_bytes())
        nat = native_sha(path)
        match = uni == nat
        ok &= match
        print(name, "OK" if match else "FAIL")
        if not match:
            print("  uni", uni)
            print("  cli", nat)

    docx = Path(r"D:/Docs/test report/0x100216 PLC offline trouble shooting.docx")
    if docx.exists():
        nat = native_sha(docx)
        golden = "BB741E73 A3136085 49B3225A C5F9B80B E0287945"
        match = nat == golden
        ok &= match
        print("docx", "OK" if match else "FAIL", "(CLI vs GUI golden)")
    else:
        print("docx SKIP (path missing)")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
