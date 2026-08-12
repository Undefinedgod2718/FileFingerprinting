# UI design

**Release:** 1.0.1 — Minecraft pixel client area (native Windows title bar).

## Legacy vs modern

| Legacy (MFC) | Modern (WPF) |
|--------------|--------------|
| Modal dialog | `MainWindow.xaml` — Minecraft pixel theme |
| Drag + menu | `AllowDrop` + `OpenFileDialog` |
| Status line | `StatusText` + emerald-block progress bar |
| Read-only key fields | Left-column labels + dark concrete text boxes + stone Copy buttons |
| In-app strings | English + Traditional Chinese (`Assets/strings-en.json`, `Assets/strings-zh-TW.json` embedded) |
| No MCP | Settings → MCP json + smoke test |

## Branding

| Item | Value |
|------|-------|
| Product name (EN) | File Fingerprinting |
| Product name (zh-TW) | 文件指紋識別 |
| Published exe | `FileFingerprinting.exe` (multi-file folder publish — see [build-app](../build/build-app.md)) |
| App version | 1.0.1 (`TpFileM.App.csproj`, Inno Setup `AppVersion`) |
| App icon | `src/TpFileM.App/Assets/logo.ico` |

## Visual theme (1.0.1 — readability pass)

| Element | Implementation |
|---------|----------------|
| Window chrome | Native OS title bar |
| Body background | Tiled `concrete_light.png` |
| Header | Tiled `concrete_green.png`; title white + dual block shadow (no header icon) |
| Field labels | Left column, `McFieldLabel` — 14px bold (`Label_FileName`, `Label_CrcKey`, `Label_ShaKey`) |
| Data fields | `concrete_dark.png`, 15px text, `McDataField` |
| Copy / footer buttons | `stone.png` tile, beveled border, white **#FFFFFF** label + 1px dark shadow (`McStoneButton`) |
| Key Mode | Spruce wood tile (`McTileSpruce`), brown border, white shadow text 14px (`McKeyModeCombo`) |
| Progress | Tiled `emerald.png` on dark concrete track |
| Tooltips | Dark concrete background; **white #FFFFFF** text, 14px Monocraft |
| Font | Monocraft bundled; fallback Courier New |
| Base font size | Window 14px; status 13px |

**Do not use** `crafting_grid.png` — removed (grid fought button text readability).

Textures: original pixel art (Minecraft-inspired). Theme: `Themes/MinecraftTheme.xaml`.

### Button style (current)

Stone slab background + beveled border; label is dual `TextBlock` (shadow offset 1,1 then white on top):

```xml
<Border Background="{StaticResource McTileStone}" BorderBrush="{StaticResource McStoneDarkBrush}" BorderThickness="3">
  <Border BorderBrush="{StaticResource McStoneLightBrush}" BorderThickness="1,1,0,0">
    <Grid>
      <TextBlock Text="{TemplateBinding Content}" Foreground="#1A1A1A" Margin="1,1,0,0"/>
      <TextBlock Text="{TemplateBinding Content}" Foreground="#FFFFFF"/>
    </Grid>
  </Border>
</Border>
```

After theme changes: **clean publish** per [release-1.0.1.md](../dev/release-1.0.1.md).

## Layout (1.0.1)

**Default window:** 760×460 px (`MinWidth` 720, `MinHeight` 420).

| Dimension | Value | Rationale |
|-----------|-------|-----------|
| Width 760 | ~728 px client | Full EN title at 22px Monocraft; footer buttons ~174 px each |
| MinWidth 720 | ~688 px client | Footer ≥~167 px/btn; title stays `Auto` width |
| Height 460 | — | Room for zh-TW status wrap + tooltip clearance |
| Label column | 120 px | Headroom for zh-TW field labels |

**Header grid:** `Auto | * | Auto` — title block keeps natural width; middle spacer shrinks; Key Mode combo (280 px) stays right-aligned. Avoids title truncation at 680 px (`*` column competed with Key Mode).

**Footer:** `UniformGrid` (4 equal stone buttons); horizontal margin 2 px per button (`McFooterButton`).

```
┌─ green concrete header ─────────────────────────────┐
│ File Fingerprinting    [spacer]    Key Mode [spruce]│
├─ light concrete body ─────────────────────────────────┤
│ File name   [────────────────────────────────]    │
│ CRC Key     [────────────────────] [Copy]           │
│ SHA Key     [────────────────────] [Copy]           │
│ ████████ emerald progress ████████                  │
│ status text                                         │
│ [Select] [Generate Key] [Settings] [Quit]           │
└─────────────────────────────────────────────────────┘
```

- **Key Mode** — Legacy enabled; Modern disabled until firmware spec.

### Size differential (EN vs zh-TW)

| Scenario | Window W | Header | Footer EN | Verdict |
|----------|----------|--------|-----------|---------|
| Old default 680×440 | 680 | Title clipped | ~162 px/btn tight | Layout squeeze |
| **Current 760×460** | 760 | Full title + spacer | ~174 px/btn OK | Stable |
| Min 720×420 | 720 | Title `Auto` intact | ~167 px/btn OK | Acceptable floor |
| Comfortable 840×480 | 840 | Spacious | ~194 px/btn | Best for long tooltips |

Do **not** use `MinWidth=600` — guarantees title clip and footer wrap.

## Settings window

Inherits global theme; light concrete background.
