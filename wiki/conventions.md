# Documentation conventions

Rules for maintaining this wiki.

## Language

| Audience | Language |
|----------|----------|
| Wiki pages (`wiki/`) | **English** |
| In-app strings | English + Traditional Chinese (`Assets/strings-en.json`, `Assets/strings-zh-TW.json`) |
| Chat / informal notes | Any (not stored in wiki) |

## User vs developer docs

| Audience | Path | Content |
|----------|------|---------|
| **End users** | `wiki/user/` | Install wizard, basic use — no TPFileM, tests, or dev tools |
| **Developers** | `wiki/dev/`, `wiki/build/`, `wiki/testing/`, etc. | Build, golden tests, RE, MCP |

Do not put developer publish steps or `TPFILEM_LEGACY_EXE` in `wiki/user/`.

Before changing Legacy SHA Key, hashing, or installer runtime — read [`wiki/dev/legacy-sha-dependency.md`](dev/legacy-sha-dependency.md).

## Three layers (do not mix)

| Layer | Location | Content |
|-------|----------|---------|
| **Behavior spec** | `wiki/implementation/`, `wiki/testing/test-vectors.md` | What modern code must output; golden values |
| **Reverse engineering (active)** | `wiki/reverse-engineering/` | Current RE conclusions still relevant to behavior |
| **Reverse engineering (archive)** | `wiki/reverse-engineering/archive/` | Superseded hypotheses and historical disasm |
| **Runbooks** | `wiki/build/`, `wiki/testing/manual-gui-parity.md` | Commands, paths, checklists |

**Rule:** Implementation docs describe *current* behavior only. When RE conclusions are overturned by golden tests, **move the full page to `archive/`** and leave a short stub at the original path.

## Archiving superseded RE

1. When golden / `dotnet test` disproves an RE narrative → move the **entire page** to `wiki/reverse-engineering/archive/`.
2. At the **original path**, leave a **stub** (≤15 lines): status, one-line conclusion, links to archive + current spec.
3. Archive page header (first line after title):

   ```markdown
   **Archived (YYYY-MM-DD)** — superseded by [page](relative-link).
   ```

4. Do **not** delete historical RE text; fix relative links inside archived files (`../../src` → `../../../src`, sibling pages → `../page.md`).
5. Active investigation pages that **resolved** correctly (e.g. `sha-gui-investigation.md`) stay on the main RE path — they are the runtime spec, not archive fodder.

### Stub template

```markdown
# Original title

**Status:** Archived (YYYY-MM-DD) — one-line why this is no longer authoritative.

- Full text: [archive/filename.md](archive/filename.md)
- Current spec: [link to active page](...)
```

## Source of truth

| Data | Canonical file |
|------|----------------|
| CRC + SHA golden values | [`tools/fixtures/legacy-golden.json`](../tools/fixtures/legacy-golden.json) |
| Automated regression | `dotnet test` + `tools/sha_parity_check.py` (dev) |
| Manual GUI sign-off | [`wiki/testing/manual-gui-parity.md`](testing/manual-gui-parity.md) sign-off table |

When golden changes: **JSON → xUnit → test-vectors.md → implementation → RE stub/archive**.

## Page headers (active pages)

| Page type | Header |
|-----------|--------|
| Resolved investigation | `**Status:** Resolved (YYYY-MM-DD) — outcome.` |
| Work in progress | `**Status:** WIP — blocker or next step.` |
| Phase 2 / pending spec | `**Status:** Phase N — PENDING (reason).` |
| Stable reference (build, architecture) | Omit unless broken |

## Linking

- Prefer **relative** links within wiki.
- Link to repo paths from wiki using relative paths (`../../src/TpFileM.Core/Hasher.cs`).
- Cross-link RE → implementation when behavior is locked.

## Evidence

| Type | Where |
|------|-------|
| GUI screenshots | `tools/fixtures/screenshots/phase{N}/` + README in that folder |
| One-off scripts | `tools/` — note publish-required vs dev-only in wiki |
| Ghidra exports | Not committed; summarize in wiki |

Screenshot names: `{fixture}-legacy.png`, `{fixture}-modern.png`.

## What to update when

| Change | Update |
|--------|--------|
| Algorithm / output | `legacy-golden.json`, tests, `test-vectors.md`, `core-algorithms.md` |
| New project or publish artifact | `README.md`, `build/build-app.md`, `overview.md` |
| UI / branding | `implementation/ui-design.md` |
| RE conclusion overturned | Archive full page; stub at old path; link from `wiki/README.md` archive section |
| Phase milestone | `overview.md`, `verification-strategy.md`, manual sign-off table |
| Release defect (fixed or open) | `dev/bug-reports.md`, `dev/release-*.md`, user troubleshooting in `user/install.md` if user-visible |
| Release milestone (x.y.z) | `dev/release-x.y.z.md`, `bug-reports.md` version matrix, `ui-design.md`, `user/install.md` |

## Forbidden in implementation docs

- Pasting Ghidra decompiler output as “the implementation”
- Claiming RFC SHA-1 for **legacy GUI output** (see `sha-gui-investigation.md`)
- Hard-coded machine-specific paths without a documented default (use `TPFILEM_LEGACY_EXE`)

## Index maintenance

Every new wiki page must be linked from [`wiki/README.md`](README.md). Archived pages are listed under **Archive** in that index.
