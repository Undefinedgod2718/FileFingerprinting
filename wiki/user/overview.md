# File Fingerprinting — overview

**File Fingerprinting** (文件指紋識別) computes two fingerprint strings for a selected file:

| Output | Format | Purpose |
|--------|--------|---------|
| **CRC Key** | 8 uppercase hex digits | File checksum (zlib CRC-32) |
| **SHA Key** | Five `%08X` words, space-separated | Secondary fingerprint for equipment workflows |

Typical use: firmware images, configuration files, or technical documents where a release process records these keys for later verification.

## Workflow

1. Select or drag-and-drop a file
2. Click **Generate Key**
3. Copy CRC Key and/or SHA Key

## Install

See [install.md](install.md) — use the setup wizard; no manual configuration.

## Key modes

| Mode | Status |
|------|--------|
| **Legacy** (CRC + SHA Key) | Available — matches established device verification |
| **Modern** (digital signature) | Coming in a future release |

## Settings

- **Language:** English or Traditional Chinese
- **Font:** Choose between the default Minecraft pixel font, Windows System font (Segoe UI), or browse for a custom `.ttf` file.
- **Auto-Update:** The application seamlessly downloads and prepares updates in the background. You will be prompted to restart when a new version is ready.
- **MCP / automation:** not included in the standard installer; available only in developer builds
