# v0.1.5 — Windows credential path

Lets the adapter run on Windows by delegating credential extraction to the
publishing skill's PowerShell launcher.

> ## ⚠️ Windows support is untested
>
> The Windows extractor lives in `bilibili-publish` v0.2.0 and has **not** been
> run on a Windows machine. Everything else in this release is macOS-tested
> behaviour.

## What changed

- `scripts/publish_bilibili_dual_cover.py` now picks the extractor by platform:
  - **macOS** → `extract_bili_login_macos.sh` (tested)
  - **Windows** → `extract_bili_login_windows.ps1` (untested, and it prints a
    warning to that effect before running)
- If the Windows extractor fails, pass `--cookies <file>` with a `cookies.json`
  you produced yourself. That path is platform-independent and unaffected by
  this change.

## Requirements

- `bilibili-publish` **v0.2.0 or newer** for the Windows script.
- Python 3.10+, `requests`, `ffprobe`, and (for extraction) `websockets`.

## Verification

```bash
python3 scripts/check_dependencies.py
```

All three external dependencies should report `OK`. On Windows the dependency
check prints the PowerShell command and repeats the untested warning.

## Release Policy

Future updates use strictly increasing semantic versions. Previous releases and
tags are retained.
