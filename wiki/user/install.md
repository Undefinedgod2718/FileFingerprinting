# Install File Fingerprinting

End-user setup for **File Fingerprinting** (文件指紋識別). No developer tools or manual file layout required.

## Requirements

- Windows 10 or 11 (64-bit)
- Administrator rights for installation (default location: `Program Files`)

## Install

1. Run **`FileFingerprinting-Setup.exe`** from your IT team or release package (this is the **only** file end users need).
2. Choose **English** or **繁體中文** when the installer language dialog appears (matches your Windows language when possible).
3. Follow the wizard (install location, optional desktop shortcut).
4. Launch **File Fingerprinting** / **文件指紋識別** from the Start menu.

## Uninstall

**Settings → Apps → Installed apps → File Fingerprinting → Uninstall**

Or use **File Fingerprinting → Uninstall** from the Start menu folder.

## Basic use

1. Click **Select a file** or drag a file onto the window.
2. Click **Generate Key**.
3. Copy **CRC Key** and **SHA Key** as needed.

Language: **Settings** → English or Traditional Chinese.

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| Install blocked | Run Setup as administrator; check corporate software policy |
| App won't start after install | Reinstall **1.0.1** Setup; need full install folder, not exe alone |
| UI looks old / dark button text | Reinstall **1.0.1** or run from fresh `publish/app` after clean rebuild — see [release notes](../dev/release-1.0.1.md) |
| Generate Key fails on SHA | Reinstall from the official Setup package (runtime files may be missing) |
| CRC works, SHA does not | Contact support — do not delete files from the install folder |

**Version note:** Installer reports **1.0.1** (2026-07-07). Older **1.0.0** packages had startup and packaging defects. Reinstall current Setup if the app will not start or UI looks outdated.

- Release summary: [release-1.0.1.md](../dev/release-1.0.1.md)
- Defect log: [bug reports](../dev/bug-reports.md)

For product overview, see [overview](overview.md).

Developer documentation is separate: [../dev/README.md](../dev/README.md).
