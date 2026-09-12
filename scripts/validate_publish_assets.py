#!/usr/bin/env python3
"""Validate A2E Bilibili delivery assets before publishing."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def probe_video(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--cover-16x9", required=True)
    parser.add_argument("--cover-4x3", required=True)
    parser.add_argument("--publish-json", required=True)
    args = parser.parse_args()

    video = Path(args.video).expanduser().resolve()
    cover_169 = Path(args.cover_16x9).expanduser().resolve()
    cover_43 = Path(args.cover_4x3).expanduser().resolve()
    config = Path(args.publish_json).expanduser().resolve()
    for label, path in (
        ("video", video),
        ("16:9 cover", cover_169),
        ("4:3 cover", cover_43),
        ("publish JSON", config),
    ):
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"{label} missing or empty: {path}")

    data = probe_video(video)
    video_streams = [
        item for item in data.get("streams", []) if item.get("codec_type") == "video"
    ]
    audio_streams = [
        item for item in data.get("streams", []) if item.get("codec_type") == "audio"
    ]
    if not video_streams:
        fail("video stream missing")
    if not audio_streams:
        fail("audio stream missing")
    v = video_streams[0]
    a = audio_streams[0]
    if (v.get("width"), v.get("height")) != (1920, 1080):
        fail(f"video must be 1920x1080, got {v.get('width')}x{v.get('height')}")
    if v.get("codec_name") != "h264":
        fail(f"video codec must be h264, got {v.get('codec_name')}")
    if a.get("codec_name") != "aac":
        fail(f"audio codec must be aac, got {a.get('codec_name')}")
    if str(a.get("sample_rate")) != "44100":
        fail(f"audio sample rate must be 44100, got {a.get('sample_rate')}")
    fps_num, fps_den = (v.get("r_frame_rate") or "0/1").split("/", 1)
    fps = float(fps_num) / float(fps_den or 1)
    if abs(fps - 30.0) > 0.01:
        fail(f"video must be 30fps, got {fps:g}")

    for label, path, expected in (
        ("16:9 cover", cover_169, (1920, 1080)),
        ("4:3 cover", cover_43, (1440, 1080)),
    ):
        with Image.open(path) as image:
            if image.size != expected:
                fail(f"{label} must be {expected[0]}x{expected[1]}, got {image.size}")
            if image.mode not in ("RGB", "RGBA"):
                fail(f"{label} has unexpected mode {image.mode}")

    try:
        metadata = json.loads(config.read_text(encoding="utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        fail(f"publish JSON is not valid UTF-8 JSON: {exc}")
    title = metadata.get("title", "")
    desc = metadata.get("desc", "")
    tags = [item.strip() for item in metadata.get("tag", "").split(",") if item.strip()]
    if not title or len(title) > 80:
        fail("title must contain 1-80 characters")
    if not desc or len(desc) > 2000:
        fail("desc must contain 1-2000 characters")
    if not 1 <= len(tags) <= 10:
        fail(f"tag must contain 1-10 comma-separated tags, got {len(tags)}")
    metadata_text = "\n".join([title, desc, *tags])
    if "\ufffd" in metadata_text or "??" in metadata_text:
        fail("metadata appears mojibake; verify UTF-8 before publishing")
    if "?" in metadata_text:
        print("WARN: metadata contains '?'; confirm it is intentional", file=sys.stderr)
    for field in ("tid",):
        if not isinstance(metadata.get(field), int):
            fail(f"{field} must be an integer")

    duration = float((data.get("format") or {}).get("duration") or 0)
    print(
        json.dumps(
            {
                "video": str(video),
                "duration_seconds": duration,
                "video": f"{v.get('width')}x{v.get('height')} {v.get('codec_name')} {fps:g}fps",
                "audio": f"{a.get('codec_name')} {a.get('sample_rate')}Hz",
                "cover_16x9": str(cover_169),
                "cover_4x3": str(cover_43),
                "title_chars": len(title),
                "desc_chars": len(desc),
                "tags": tags,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
