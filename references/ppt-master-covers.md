# PPT Master Dual Covers

The 16:9 main cover and 4:3 secondary cover share content and visual language
but are composed separately.

## Canvas contract

| Variant | Canvas | Bilibili field |
|---|---|---|
| 16:9 | `1920×1080` | `cover` |
| 4:3 | `1440×1080` | `cover43` |

PPT Master's registered `banner` canvas is suitable for the 16:9 version. For
4:3, use a custom `0 0 1440 1080` project SVG. Do not render the registered
`ppt43` canvas at `1024×768` and upscale it.

## Cover brief

Create `cover_brief.md` inside the PPT Master project:

```markdown
# Cover Brief

- Topic:
- Audience:
- Main title:
- Subtitle:
- One-sentence hook:
- Three factual proof points:
- Visual metaphor:
- Palette:
- Forbidden:

## 16:9 composition

## 4:3 composition
```

The 4:3 version should reduce horizontal elements, enlarge the hero subject,
and rewrap text rather than inheriting the 16:9 coordinates.

## PPT Master commands

Resolve the dependency root first:

```bash
export PPT_MASTER_DIR="${PPT_MASTER_DIR:-$HOME/ppt-master/skills/ppt-master}"
export PPT_PY="${PPT_PY:-python3}"
```

Create a Quick Generate project:

```bash
"$PPT_PY" "$PPT_MASTER_DIR/scripts/project_manager.py" init \
  "<slug>_covers" --dir "<covers_project_root>" \
  --quick-generate --format banner
```

Put the authored cover SVGs in `svg_output/`. Validate the final roster:

```bash
"$PPT_PY" "$PPT_MASTER_DIR/scripts/svg_quality_checker.py" \
  "<project_path>" --stage final --quick-generate --json
```

Export the editable PPTX:

```bash
"$PPT_PY" "$PPT_MASTER_DIR/scripts/svg_to_pptx.py" \
  "<project_path>" --quick-generate \
  -o "<project_path>/exports/covers.pptx"
```

## PNG rendering

Use PPT Master's preview/export flow when available. If its live-preview
service is not running, render each SVG with the portable helper in this
repository:

```bash
python3 scripts/render_svg_cover.py \
  --svg "<project>/svg_output/cover_16x9.svg" \
  --out "<project>/covers/cover_16x9.png" \
  --width 1920 --height 1080

python3 scripts/render_svg_cover.py \
  --svg "<project>/svg_output/cover_4x3.svg" \
  --out "<project>/covers/cover_4x3.png" \
  --width 1440 --height 1080
```

Set `CHROME_PATH` when Chrome/Chromium is installed in a non-standard
location.

## Acceptance checks

- Main cover is exactly `1920×1080`.
- Secondary cover is exactly `1440×1080`.
- Neither PNG is blank or all-background.
- Text is not clipped and fonts are present.
- The two covers are related but not simple crops of each other.

