"""Automate legacy TPFileM.exe to read CRC/SHA for a file path."""
from __future__ import annotations

import time
from pathlib import Path

from pywinauto import Application

LEGACY_EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
FILE_PATH = Path(r"D:\Docs\test report\0x100216 PLC offline trouble shooting.docx")


def main() -> int:
    if not LEGACY_EXE.exists():
        print("LEGACY_EXE_MISSING")
        return 1
    if not FILE_PATH.exists():
        print("FILE_MISSING")
        return 1

    app = Application(backend="win32").start(str(LEGACY_EXE))
    time.sleep(2)
    dlg = app.window(title="Delta Telecom Power File Monitor")
    dlg.wait("visible", timeout=10)

    dlg.child_window(title="&Select a file", class_name="Button").click_input()
    time.sleep(1)

    file_dlg = app.window(class_name="#32770", title="Open")
    if not file_dlg.exists(timeout=2):
        file_dlg = app.window(class_name="#32770", found_index=1)
    file_dlg.wait("visible", timeout=8)
    file_dlg.Edit.set_edit_text(str(FILE_PATH))
    time.sleep(0.3)
    file_dlg.child_window(title="Open", class_name="Button").click_input()
    time.sleep(0.8)

    dlg.child_window(title="Generate Key", class_name="Button").click_input()

    crc_edit = dlg.child_window(best_match="CRC KeyEdit")
    sha_edit = dlg.child_window(best_match="SHA KeyEdit")

    for _ in range(80):
        time.sleep(0.25)
        crc = crc_edit.window_text().strip()
        sha = sha_edit.window_text().strip()
        if crc and crc != "0" and sha and sha != "0":
            print("LEGACY_FILE", FILE_PATH)
            print("LEGACY_CRC", crc)
            print("LEGACY_SHA", sha)
            app.kill()
            return 0

    print("LEGACY_TIMEOUT")
    print("LEGACY_CRC", crc_edit.window_text())
    print("LEGACY_SHA", sha_edit.window_text())
    app.kill()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
