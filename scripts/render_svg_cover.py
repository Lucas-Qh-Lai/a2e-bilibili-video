#!/usr/bin/env python3
"""Render a PPT Master cover SVG at an exact output size with headless Chrome."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)


def find_chrome(explicit: str | None) -> str:
    if explicit:
        if Path(explicit).is_file():
            return explicit
        raise SystemExit(f"Chrome executable not found: {explicit}")
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    found = shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise SystemExit("Chrome/Chromium not found; pass --chrome")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--svg", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--chrome")
    args = parser.parse_args()

    svg = Path(args.svg).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    if not svg.is_file():
        raise SystemExit(f"SVG not found: {svg}")
    out.parent.mkdir(parents=True, exist_ok=True)
    chrome = find_chrome(args.chrome)
    url = svg.as_uri()
    with tempfile.TemporaryDirectory(prefix="a2e-cover-chrome-") as run_dir:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={run_dir}",
            f"--window-size={args.width},{args.height}",
            f"--screenshot={out}",
            url,
        ]
        print("+", " ".join(cmd), flush=True)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if out.is_file() and out.stat().st_size > 0:
                break
            if process.poll() is not None:
                break
            time.sleep(0.2)
        if out.is_file() and out.stat().st_size > 0:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        else:
            process.kill()
            process.wait()
            raise SystemExit("Chrome did not create a non-empty PNG")
    if not out.is_file() or out.stat().st_size == 0:
        raise SystemExit(f"Chrome did not create a non-empty PNG: {out}")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
