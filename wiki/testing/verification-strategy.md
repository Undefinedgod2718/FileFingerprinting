# Verification strategy

## Layers

1. **xUnit golden tests** — `tools/fixtures/legacy-golden.json` (CRC + SHA per fixture)
2. **SHA parity script** — `tools/sha_parity_check.py` (CLI vs Unicorn oracle; dev-only)
3. **Fixture generation** — `tools/legacy_probe.ps1`
4. **Manual legacy GUI** — optional screenshots; required sign-off for paths outside repo ([manual-gui-parity](manual-gui-parity.md))

Phase 1 status (2026-07-07): repo fixtures **locked** by `dotnet test -c Release` (9/9).

## Publish smoke (GUI)

After `.\tools\publish.ps1`, launch `publish/app/FileFingerprinting.exe` and confirm:

1. Window stays open (no immediate exit — FF-001, FF-002)
2. `deps.json` reports `FileFingerprinting/1.0.1`
3. `Assets/Textures/crafting_grid.png` and `Assets/Fonts/Monocraft.ttf` exist beside exe
4. Button labels white on **stone** (not grid); Key Mode spruce readable; field labels visible (FF-004–FF-007)

Failures: [bug reports](../dev/bug-reports.md). Do not treat a ~140 MB lone exe as valid. If UI looks stale, clean rebuild per [release-1.0.1.md](../dev/release-1.0.1.md).

## Correctness criterion

> Same file bytes → same CRC Key and SHA Key strings as legacy GUI.

Implementation may differ (zlib CRC in-process; SHA via native helper); **output** must match.

## Not used for legacy SHA

- RFC SHA-1 (`SHA1.HashData`) — wrong digest for GUI golden; see [sha-gui-investigation](../reverse-engineering/sha-gui-investigation.md)
