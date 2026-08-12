"""Dump legacy TPFileM dialog controls."""
import time
from pathlib import Path
from pywinauto import Application

LEGACY_EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
app = Application(backend="win32").start(str(LEGACY_EXE))
time.sleep(2)
dlg = app.top_window()
print("TITLE:", dlg.window_text())
dlg.print_control_identifiers(depth=3)
app.kill()
