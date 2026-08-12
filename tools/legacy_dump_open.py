import time
from pathlib import Path
from pywinauto import Application

LEGACY_EXE = Path(r"D:\Program_Coding\Q_Test\TPFileM\TPFileM.exe")
app = Application(backend="win32").start(str(LEGACY_EXE))
time.sleep(2)
dlg = app.window(title="Delta Telecom Power File Monitor")
dlg.child_window(title="&Select a file", class_name="Button").click_input()
time.sleep(2)
print("TOP:", app.top_window().window_text())
try:
    dlg.print_control_identifiers(depth=4)
except Exception as e:
    print(e)
# try all windows in app
for w in app.windows():
    print("WIN", w.handle, repr(w.window_text()))
app.kill()
