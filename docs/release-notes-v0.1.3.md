# v0.1.3 — Publishing delegated to bilibili-publish

This release splits publishing out of the A2E wrapper. Production still lives
in this repository; publishing now belongs to a separate skill.

## What changed

- **Delegated publishing.** The adapter no longer imports the upstream
  `bilibili-ai-video` publishing module. It runs the delivery-asset validator,
  then invokes the standalone
  [`bilibili-publish`](https://github.com/Lucas-Qh-Lai/bilibili-publish) skill
  through its command-line entry point.
- **Native dual covers.** The 4:3 cover is passed with `--cover43`, which
  `bilibili-publish` supports natively. The previous session-level shim that
  injected `cover43` into the `add/v3` payload is gone.
- **New path variable.** `BILIBILI_PUBLISH_SKILL_DIR` (default
  `$CODEX_HOME/skills/bilibili-publish`). `BILIBILI_SKILL_DIR` is still read as
  a fallback.
- **Clearer receipts.** `delivery/bilibili/publish_result.json` now records
  `published_by`.

## Why

A2E owns production: research, narration, timeline, Remotion shots, QC, and
the 1920×1080 delivery render. Publishing is a different job with a different
failure surface. Keeping it in its own skill means:

- the upload chain can be updated without touching the production wrapper;
- the boundary is a stable CLI contract instead of imported internals;
- anyone can use the publishing skill without installing the production stack,
  and vice versa.

## Install

```bash
git clone https://github.com/Lucas-Qh-Lai/bilibili-publish.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/bilibili-publish"

git clone https://github.com/Lucas-Qh-Lai/a2e-bilibili-video.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/a2e-bilibili-video"
```

Then verify:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export A2E_SKILL_DIR="$CODEX_HOME/skills/anything2explainer"
export BILIBILI_PUBLISH_SKILL_DIR="$CODEX_HOME/skills/bilibili-publish"
export PPT_MASTER_DIR="$HOME/ppt-master/skills/ppt-master"

python3 scripts/check_dependencies.py
```

## Attribution

The Bilibili publishing flow used by this release was refactored from
[sukai213/bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
(`skills/bilibili-ai-video`), by [sukai213](https://github.com/sukai213).

That repository has **no LICENSE file**. Its README states that its skills and
scripts are for personal learning and automation-workflow reference only — a
restrictive notice, not an open-source license. To respect the author,
`bilibili-publish` rewrote the publishing scripts and documentation as an
independent implementation rather than copying them, and retains full
attribution in its README and `THIRD_PARTY_NOTICES.md`.

This repository does not bundle or redistribute either project's source code;
it invokes `bilibili-publish`'s CLI at runtime.

## Release Policy

Future updates use strictly increasing semantic versions. Previous releases and
tags are retained.
