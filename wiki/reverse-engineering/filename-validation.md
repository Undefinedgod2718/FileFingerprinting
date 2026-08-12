# Filename validation

## Legacy behavior (observed)

| Step | Function | On failure |
|------|----------|------------|
| Open file for CRC | `0x00401C30` | Message `File name Error!` (`0x41D160`) |
| Open file for SHA | `0x004021F0` → `CreateFile` | Message `File name Error in SHA!` (`0x41D228`) |

The SHA-labeled error is shown when the **second `CreateFile` call fails** after CRC succeeded — typically the same path, so in practice this maps to **file not readable / sharing / access** rather than parsing SHA from the filename.

## Modern mapping

[`FilenameValidator.cs`](../../src/TpFileM.Core/FilenameValidator.cs):

| Result | Legacy-style message |
|--------|----------------------|
| `Empty` | Step #1: Please select a file… |
| `NotFound` | File name Error! |
| `NotReadable` | File name Error in SHA! |
| `Ok` | *(proceed)* |

## [WIP]

If production TP files require **embedded hash tokens in the filename**, capture vectors from real hardware files and extend the validator.
