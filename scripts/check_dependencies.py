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


def resolve_publish_root() -> Path:
    """Locate the bilibili-publish skill across the shared agent stores."""
    return resolve_skill(
        "bilibili-publish",
        ("BILIBILI_PUBLISH_SKILL_DIR", "BILIBILI_SKILL_DIR"),
    )


def skill_search_paths(name: str) -> list[Path]:
    """Candidate locations for a skill, in priority order.

    `~/.codex/skills` is Codex's native directory; `~/.agents/skills` is the
    shared cross-agent store that the skills CLI manages (also reachable as
    `~/.claude/skills`). The rest are per-agent mirrors.
    """
    home = Path.home()
    return [
        codex_home() / "skills" / name,
        home / ".agents" / "skills" / name,
        home / ".claude" / "skills" / name,
        home / ".config" / "opencode" / "skills" / name,
    ]


def resolve_skill(name: str, env_names: tuple[str, ...] = ()) -> Path:
    for env_name in env_names:
        configured = os.environ.get(env_name)
        if configured:
            return Path(configured).expanduser().resolve()
    for candidate in skill_search_paths(name):
        if (candidate / "SKILL.md").is_file():
            return candidate.resolve()
    return skill_search_paths(name)[0]


def main() -> int:
    roots = {
        "A2E": resolve_skill("anything2explainer", ("A2E_SKILL_DIR",)),
        "Bilibili publish": resolve_publish_root(),
        # PPT Master is a standalone repo, not a skill in the agent stores.
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
