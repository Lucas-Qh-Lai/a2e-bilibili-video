#!/usr/bin/env python3
"""Publish a validated video with separate 16:9 and 4:3 Bilibili covers."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def bilibili_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    configured = os.environ.get("BILIBILI_SKILL_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return codex_home() / "skills" / "bilibili-ai-video"


def default_python() -> Path:
    """Prefer this skill's local environment when it has the validator deps."""
    local_python = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"
    if local_python.is_file():
        return local_python
    return Path(sys.executable)


def load_module(path: Path):
    if not path.is_file():
        raise SystemExit(f"Missing upstream module: {path}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Unable to import upstream module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DualCoverSession:
    """Proxy an upstream requests session and inject cover43 on add/v3."""

    def __init__(self, upstream_session, cover43_url: str):
        self._upstream_session = upstream_session
        self._cover43_url = cover43_url

    def __getattr__(self, name):
        return getattr(self._upstream_session, name)

    def post(self, url: str, *args, **kwargs):
        if "/x/vu/web/add/v3" in url and isinstance(kwargs.get("json"), dict):
            kwargs["json"] = {
                **kwargs["json"],
                "cover43": self._cover43_url,
            }
        return self._upstream_session.post(url, *args, **kwargs)


def run_validator(python: Path, args: argparse.Namespace) -> None:
    validator = Path(__file__).with_name("validate_publish_assets.py")
    subprocess.run(
        [
            str(python),
            str(validator),
            "--video",
            str(args.video),
            "--cover-16x9",
            str(args.cover_16x9),
            "--cover-4x3",
            str(args.cover_4x3),
            "--publish-json",
            str(args.config),
        ],
        check=True,
    )


def extract_cookies(upstream: Path, cookies: str | None) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    if cookies:
        path = Path(cookies).expanduser().resolve()
        if not path.is_file():
            raise SystemExit(f"Cookie file not found: {path}")
        return path, None

    extractor = upstream / "extract_bili_login_macos.sh"
    if not extractor.is_file():
        raise SystemExit(
            "--cookies was omitted, but the upstream macOS extractor is missing: "
            f"{extractor}"
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
    parser.add_argument("--bilibili-skill-dir")
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

    upstream_root = bilibili_root(args.bilibili_skill_dir)
    upstream_scripts = upstream_root / "scripts"
    publisher = load_module(upstream_scripts / "publish_bilibili.py")
    verifier = upstream_scripts / "verify_published.py"
    if not verifier.is_file():
        raise SystemExit(f"Missing upstream verifier: {verifier}")

    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    cookie_path, temp = extract_cookies(upstream_scripts, args.cookies)
    try:
        cookies = json.loads(cookie_path.read_text(encoding="utf-8-sig"))
        csrf = cookies.get("bili_jct")
        if not csrf:
            raise SystemExit("Cookie extraction did not return bili_jct")

        session = publisher.make_session(cookies)
        cover_url = publisher.step_cover(session, str(args.cover_16x9), csrf)
        cover43_url = publisher.step_cover(session, str(args.cover_4x3), csrf)
        pre = publisher.step_preupload(
            session, args.video.name, args.video.stat().st_size
        )
        upload_id, upos_url = publisher.step_meta(
            pre, args.video.stat().st_size
        )
        etags, chunks = publisher.step_chunks(
            upos_url,
            pre["auth"],
            upload_id,
            str(args.video),
            args.video.stat().st_size,
            pre["chunk_size"],
        )
        publisher.step_finalize(
            upos_url,
            pre["auth"],
            upload_id,
            pre["biz_id"],
            args.video.name,
            etags,
            chunks,
        )
        stem = Path(pre["upos_uri"]).stem

        data = publisher.step_submit(
            DualCoverSession(session, cover43_url),
            config,
            cover_url,
            stem,
            pre["biz_id"],
            csrf,
        )

        result_path = (
            args.project / "delivery" / "bilibili" / "publish_result.json"
        )
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(
            json.dumps(
                {
                    "bvid": data.get("bvid"),
                    "aid": data.get("aid"),
                    "cover": cover_url,
                    "cover43": cover43_url,
                    "title": config["title"],
                    "published_at": time.time(),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        bvid = data.get("bvid")
        print(f"Published: https://www.bilibili.com/video/{bvid}")

        if not args.skip_public_wait:
            print("Waiting 120 seconds before public verification.")
            time.sleep(120)
        subprocess.run(
            [
                str(python),
                str(verifier),
                "--bvid",
                str(bvid),
                "--cookies",
                str(cookie_path),
            ],
            check=False,
        )
    finally:
        if temp is not None:
            temp.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
