"""Read legacy GUI CRC/SHA for digits.bin."""
from __future__ import annotations

import time
from pathlib import Path

from pywinauto import Application

LEGACY_EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
FILE_PATH = Path(r"D:\Program_Coding\Q_Test\tpfilem-modern\tools\fixtures\digits.bin")


def main() -> int:
    app = Application(backend="win32").start(str(LEGACY_EXE))
    time.sleep(2)
    dlg = app.window(title="Delta Telecom Power File Monitor")
    dlg.wait("visible", timeout=10)
    dlg.child_window(title="&Select a file", class_name="Button").click_input()
    time.sleep(1)
    file_dlg = app.window(class_name="#32770", title="Open")
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
        if crc and sha and crc != "0":
            print("CRC", crc)
            print("SHA", sha)
            app.kill()
            return 0
    print("TIMEOUT")
    app.kill()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
