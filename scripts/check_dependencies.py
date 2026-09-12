#!/usr/bin/env python3
"""Check whether the external projects and local tools are available."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def resolve(env_name: str, fallback: Path) -> Path:
    return Path(os.environ.get(env_name, fallback)).expanduser().resolve()


def main() -> int:
    roots = {
        "A2E": resolve(
            "A2E_SKILL_DIR", codex_home() / "skills" / "anything2explainer"
        ),
        "Bilibili": resolve(
            "BILIBILI_SKILL_DIR", codex_home() / "skills" / "bilibili-ai-video"
        ),
        "PPT Master": resolve(
            "PPT_MASTER_DIR", Path.home() / "ppt-master" / "skills" / "ppt-master"
        ),
    }
    failures: list[str] = []
    print("External skill dependencies:")
    for name, root in roots.items():
        marker = root / "SKILL.md"
        status = "OK" if marker.is_file() else "MISSING"
        print(f"  {name:12} {status:7} {root}")
        if status == "MISSING":
            failures.append(f"{name}: expected {marker}")

    tools = {
        "node": shutil.which("node"),
        "npx": shutil.which("npx"),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
    }
    print("\nCommand-line tools:")
    for name, path in tools.items():
        print(f"  {name:12} {'OK' if path else 'MISSING':7} {path or ''}")
        if not path:
            failures.append(f"{name}: command not found")

    optional_chrome = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    chrome = os.environ.get("CHROME_PATH")
    if chrome and Path(chrome).is_file():
        chrome_path = chrome
    else:
        chrome_path = next(
            (str(path) for path in optional_chrome if path.is_file()), None
        )
    print("\nOptional SVG renderer:")
    print(f"  Chrome       {'OK' if chrome_path else 'OPTIONAL'} {chrome_path or ''}")

    if failures:
        print("\nDependency check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("\nAll required dependencies are available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
