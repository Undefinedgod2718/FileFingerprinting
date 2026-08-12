# Overview

> **End users:** see [File Fingerprinting overview](user/overview.md) and [install](user/install.md).  
> **SHA dependency:** developers must read [dev/legacy-sha-dependency.md](dev/legacy-sha-dependency.md).

## Domain context

The shipped product is **File Fingerprinting** (文件指紋識別). Internally the repo is `tpfilem-modern`; it replaces a legacy **32-bit MFC** utility (**TPFileM**) used in telecom power / industrial equipment workflows.

| Output | Format | Role |
|--------|--------|------|
| **CRC Key** | 8 uppercase hex digits | zlib / PKZIP CRC-32 over file bytes |
| **SHA Key** | five `%08X` words, space-separated | Legacy custom digest (not RFC SHA-1) |

An operator selects a file (firmware image, configuration, technical document, etc.), presses **Generate Key**, and copies two fingerprint strings. Downstream systems or devices use these values to verify that a file matches what was authorized at build or release time.

| Mode | Security | Status |
|------|----------|--------|
| **Legacy** (CRC + SHA Key) | Checksum-level — not tamper-proof | Phase 1 — locked to original `TPFileM.exe` GUI output |
| **Modern** (RSA-2048 PKI) | Digital signature over SHA-256 | Phase 2 — pending firmware spec ([modern-key-spec](security/modern-key-spec.md)) |

**tpfilem-modern** preserves Legacy output bit-for-bit on Win10/11 x64, adds automated tests and MCP automation, and documents behavior in this wiki. It does not reinvent the legacy algorithms in C# where golden parity required native code (SHA).

## Purpose

Replace a legacy **32-bit MFC** key-generation utility with a **64-bit .NET** application that:

1. Runs on modern Windows (10/11) without compatibility issues
2. Preserves legacy **CRC Key** and **SHA Key** output behavior
3. Documents reverse-engineered behavior in this wiki
4. Exposes core operations via an MCP server for LLM automation

## Legacy artifact

| Property | Value |
|----------|-------|
| Path | `../TPFileM/TPFileM.exe` |
| Size | 143,360 bytes |
| Platform | Win32 x86, MFC 4.2 static |
| UI | Single dialog: file select, CRC Key, SHA Key, Generate Key |

## Modern stack

| Component | Technology |
|-----------|------------|
| Core | C# / .NET 10 — zlib CRC + legacy SHA orchestration |
| Legacy SHA | `TpFileM.LegacySha.Cli` (win-x86; maps `TPFileM.exe`) |
| GUI | WPF → `FileFingerprinting.exe` (`Assets/logo.ico`) |
| Tests | xUnit + `legacy-golden.json` |
| MCP | stdio JSON-RPC (`TpFileM.Mcp`) |
| RE | Capstone / Unicorn (dev) + optional Ghidra MCP |

**Phase 1 (done):** Legacy CRC + SHA parity with GUI golden. **Phase 2 (pending):** Modern PKI — [modern-key-spec](security/modern-key-spec.md).

## Workflow

1. Select or drag-and-drop a file
2. Validate path / readability
3. Press **Generate Key**
4. Display **CRC Key** (`%08X`) and **SHA Key** (five `%08X` words, space-separated)
