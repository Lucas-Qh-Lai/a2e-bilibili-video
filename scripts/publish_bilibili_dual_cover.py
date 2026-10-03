#!/usr/bin/env python3
"""Publish a validated video with separate 16:9 and 4:3 Bilibili covers.

This adapter does not implement the upload itself. It validates the delivery
assets, then hands the actual publishing off to the standalone
``bilibili-publish`` skill by invoking its command-line entry point.

Keeping the upload in its own skill means A2E owns production and
``bilibili-publish`` owns publishing, with a stable CLI contract between them.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PUBLISH_SKILL_NAME = "bilibili-publish"


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def candidate_roots() -> list[Path]:
    """Where `bilibili-publish` may live, in priority order.

    On this machine the shared cross-agent store (~/.agents/skills) is the
    canonical location for CLI-managed skills, while ~/.codex/skills holds
    Codex-only ones. Both are checked so the adapter works either way.
    """
    home = Path.home()
    return [
        codex_home() / "skills" / PUBLISH_SKILL_NAME,
        home / ".agents" / "skills" / PUBLISH_SKILL_NAME,
        home / ".claude" / "skills" / PUBLISH_SKILL_NAME,
        home / ".config" / "opencode" / "skills" / PUBLISH_SKILL_NAME,
    ]


def publish_skill_root(explicit: str | None) -> Path:
    """Resolve the bilibili-publish skill directory."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    configured = os.environ.get("BILIBILI_PUBLISH_SKILL_DIR") or os.environ.get(
        "BILIBILI_SKILL_DIR"
    )
    if configured:
        return Path(configured).expanduser().resolve()
    for candidate in candidate_roots():
        if (candidate / "scripts" / "publish_bilibili.py").is_file():
            return candidate.resolve()
    return candidate_roots()[0]


def default_python() -> Path:
    """Prefer this skill's local environment when it has the validator deps."""
    local_python = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
    if local_python.is_file():
        return local_python
    return Path(sys.executable)


def require(path: Path, label: str) -> Path:
    if not path.is_file():
        raise SystemExit(f"Missing {label}: {path}")
    return path


def run_validator(python: Path, args: argparse.Namespace) -> None:
    validator = Path(__file__).with_name("validate_publish_assets.py")
    subprocess.run(
        [
            str(python),
            str(validator),
            "--video", str(args.video),
            "--cover-16x9", str(args.cover_16x9),
            "--cover-4x3", str(args.cover_4x3),
            "--publish-json", str(args.config),
        ],
        check=True,
    )


def extract_cookies(publish_scripts: Path, cookies: str | None):
    """Reuse the publishing skill's CDP extractor when no cookies are given.

    macOS uses the tested shell script. Windows uses the PowerShell launcher,
    which is provided but **untested** (see the publishing skill's
    references/windows-cookies.md).
    """
    if cookies:
        path = Path(cookies).expanduser().resolve()
        if not path.is_file():
            raise SystemExit(f"Cookie file not found: {path}")
        return path, None

    if sys.platform == "win32":
        windows_extractor = publish_scripts / "extract_bili_login_windows.ps1"
        extractor = require(
            windows_extractor, "bilibili-publish Windows credential extractor"
        )
        print(
            "Note: the Windows credential extractor is UNTESTED. "
            "If it fails, pass --cookies with a cookies.json you extracted yourself."
        )
        temp = tempfile.TemporaryDirectory(prefix="a2e-bilibili-")
        path = Path(temp.name) / "cookies.json"
        subprocess.run(
            [
                "powershell", "-ExecutionPolicy", "Bypass",
                "-File", str(extractor),
                "-Port", "9222",
                "-Out", str(path),
            ],
            check=True,
        )
        return path, temp

    extractor = require(
        publish_scripts / "extract_bili_login_macos.sh",
        "bilibili-publish credential extractor",
    )
    temp = tempfile.TemporaryDirectory(prefix="a2e-bilibili-")
    path = Path(temp.name) / "cookies.json"
    subprocess.run([str(extractor), "9222", str(path)], check=True)
    return path, temp


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--video", required=True)
    parser.add_argument("--cover-16x9", required=True)
    parser.add_argument("--cover-4x3", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--cookies")
    parser.add_argument("--bilibili-skill-dir",
                        help=f"Path to the {PUBLISH_SKILL_NAME} skill")
    parser.add_argument("--python", default=str(default_python()))
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--skip-public-wait", action="store_true")
    args = parser.parse_args()

    args.project = Path(args.project).expanduser().resolve()
    args.video = Path(args.video).expanduser().resolve()
    args.cover_16x9 = Path(args.cover_16x9).expanduser().resolve()
    args.cover_4x3 = Path(args.cover_4x3).expanduser().resolve()
    args.config = Path(args.config).expanduser().resolve()
    # Do not resolve symlinks here: a venv's `bin/python` intentionally points
    # at the base interpreter, but resolving it would discard the venv context.
    python = Path(args.python).expanduser()

    run_validator(python, args)
    if args.validate_only:
        return 0

    root = publish_skill_root(args.bilibili_skill_dir)
    scripts = root / "scripts"
    publisher = require(scripts / "publish_bilibili.py", "bilibili-publish publisher")
    verifier = require(scripts / "verify_published.py", "bilibili-publish verifier")

    cookie_path, temp = extract_cookies(scripts, args.cookies)
    try:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))

        command = [
            str(python), str(publisher),
            "--video", str(args.video),
            "--cover", str(args.cover_16x9),
            "--cover43", str(args.cover_4x3),
            "--cookies", str(cookie_path),
            "--config", str(args.config),
        ]
        print("Delegating publish to bilibili-publish:", " ".join(command))
        subprocess.run(command, check=True)

        # bilibili-publish writes publish_result.json next to its config.
        upstream_result = args.config.parent / "publish_result.json"
        result = json.loads(upstream_result.read_text(encoding="utf-8")) if upstream_result.is_file() else {}
        data = result.get("data") or {}
        bvid = data.get("bvid") or result.get("bvid")
        if not bvid:
            raise SystemExit(
                "bilibili-publish finished but no bvid was found in "
                f"{upstream_result}"
            )

        result_path = args.project / "delivery" / "bilibili" / "publish_result.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(
            json.dumps(
                {
                    "bvid": bvid,
                    "aid": data.get("aid") or result.get("aid"),
                    "cover": result.get("cover"),
                    "cover43": result.get("cover43"),
                    "title": config.get("title"),
                    "published_at": time.time(),
                    "published_by": PUBLISH_SKILL_NAME,
                },
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"Published: https://www.bilibili.com/video/{bvid}")

        if not args.skip_public_wait:
            print("Waiting 120 seconds before public verification.")
            time.sleep(120)
        subprocess.run(
            [str(python), str(verifier),
             "--bvid", str(bvid), "--cookies", str(cookie_path)],
            check=False,
        )
        print(f"Delivery receipt: {result_path}")
        return 0
    finally:
        if temp is not None:
            temp.cleanup()


if __name__ == "__main__":
    sys.exit(main())
