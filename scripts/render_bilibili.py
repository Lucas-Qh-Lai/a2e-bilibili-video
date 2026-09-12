#!/usr/bin/env python3
"""Render an A2E project at 1920x1080 from its 1280x720 design coordinates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def read_slug(project: Path) -> str:
    text = (project / "src" / "config.ts").read_text(encoding="utf-8")
    match = re.search(r"slug:\s*'([^']+)'", text)
    if not match:
        raise SystemExit("Unable to read VIDEO.slug from src/config.ts")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not (project / "package.json").is_file():
        raise SystemExit(f"Not an A2E project: {project}")
    if shutil.which("npx") is None:
        raise SystemExit("npx is required")
    if (project / "src" / "common" / "lib.tsx").is_file():
        lib = (project / "src" / "common" / "lib.tsx").read_text(encoding="utf-8")
        if "export const W = 1280" not in lib or "export const H = 720" not in lib:
            raise SystemExit("This flow expects the A2E 1280x720 design canvas")

    slug = read_slug(project)
    render_dir = project / "renders"
    raw = render_dir / f"{slug}_bilibili_{args.version}.raw.mp4"
    out = render_dir / f"{slug}_bilibili_{args.version}.mp4"
    delivery_dir = project / "delivery" / "bilibili"
    render_dir.mkdir(parents=True, exist_ok=True)
    delivery_dir.mkdir(parents=True, exist_ok=True)

    if out.exists() and not args.force:
        raise SystemExit(f"Output exists; pass --force to replace: {out}")
    if out.exists():
        out.unlink()

    run(
        [
            "npx",
            "remotion",
            "render",
            "src/index.ts",
            "Video",
            str(raw),
            "--codec=h264",
            "--crf=16",
            f"--concurrency={args.concurrency}",
            "--scale=1.5",
            "--timeout=300000",
            "--log=error",
        ],
        project,
    )
    if not raw.is_file() or raw.stat().st_size == 0:
        raise SystemExit("Remotion reported success but no output exists")

    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(raw),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "44100",
            "-movflags",
            "+faststart",
            str(out),
        ],
        project,
    )
    if not out.is_file() or out.stat().st_size == 0:
        raise SystemExit("Audio normalization reported success but no output exists")
    raw.unlink()

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,width,height,r_frame_rate,codec_name,sample_rate",
            "-of",
            "json",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    streams = json.loads(probe.stdout).get("streams") or []
    video_streams = [item for item in streams if item.get("codec_type") == "video"]
    audio_streams = [item for item in streams if item.get("codec_type") == "audio"]
    if not video_streams:
        raise SystemExit("ffprobe found no video stream")
    if not audio_streams:
        raise SystemExit("ffprobe found no audio stream")
    stream = video_streams[0]
    audio_stream = audio_streams[0]
    if (stream.get("width"), stream.get("height")) != (1920, 1080):
        raise SystemExit(
            f"Expected 1920x1080, got {stream.get('width')}x{stream.get('height')}"
        )
    if stream.get("codec_name") != "h264":
        raise SystemExit(f"Expected h264 video, got {stream.get('codec_name')}")
    if audio_stream.get("codec_name") != "aac":
        raise SystemExit(f"Expected aac audio, got {audio_stream.get('codec_name')}")
    if str(audio_stream.get("sample_rate")) != "44100":
        raise SystemExit(
            f"Expected 44100 Hz audio, got {audio_stream.get('sample_rate')}"
        )

    receipt = {
        "project": str(project),
        "slug": slug,
        "version": args.version,
        "video": str(out),
        "width": stream.get("width"),
        "height": stream.get("height"),
        "fps": stream.get("r_frame_rate"),
        "video_codec": stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "audio_sample_rate": int(audio_stream.get("sample_rate")),
        "size_bytes": out.stat().st_size,
        "render_scale": 1.5,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    receipt_path = delivery_dir / f"{slug}_delivery.json"
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Rendered: {out}")
    print(f"Receipt:  {receipt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
