# Bilibili Publishing and Verification

The adapter delegates publishing to a separately installed
`bilibili-publish` skill. Neither that skill nor its upstream is bundled or
redistributed by this repository.

## Dependencies

Resolve the publishing skill directory:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export BILIBILI_PUBLISH_SKILL_DIR="${BILIBILI_PUBLISH_SKILL_DIR:-$CODEX_HOME/skills/bilibili-publish}"
```

`bilibili-publish` 可以在以下任一位置，按优先级查找：

```text
$CODEX_HOME/skills/bilibili-publish
~/.agents/skills/bilibili-publish
~/.claude/skills/bilibili-publish
~/.config/opencode/skills/bilibili-publish
```

`BILIBILI_PUBLISH_SKILL_DIR` 仍然优先于以上全部。


Expected files:

```text
$BILIBILI_PUBLISH_SKILL_DIR/scripts/extract_bili_login_macos.sh
$BILIBILI_PUBLISH_SKILL_DIR/scripts/publish_bilibili.py
$BILIBILI_PUBLISH_SKILL_DIR/scripts/verify_published.py
```

Install it from <https://github.com/Lucas-Qh-Lai/bilibili-publish>:

```bash
git clone https://github.com/Lucas-Qh-Lai/bilibili-publish.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/bilibili-publish"
```

On macOS, the extractor uses the logged-in Bilibili desktop app through CDP.
The app is restarted briefly with a debugging port. On other platforms,
provide an existing cookie JSON file with `--cookies`.

## How the hand-off works

The adapter does not implement the upload itself. It validates the delivery
assets, then invokes the publishing skill's command-line entry point:

```bash
python3 "$BILIBILI_PUBLISH_SKILL_DIR/scripts/publish_bilibili.py" \
  --video <final.mp4> \
  --cover <cover-16x9.png> \
  --cover43 <cover-4x3.png> \
  --cookies <cookies.json> \
  --config <publish.json>
```

`bilibili-publish` handles the whole upload chain and natively supports the
4:3 cover through `--cover43`, so no session-level shim is needed. It writes
`publish_result.json` next to the config file; the adapter reads that back,
copies the `bvid` into `delivery/bilibili/publish_result.json`, then runs the
verification step.

## Upload sequence

1. Upload the 16:9 cover and keep its returned URL as `cover`.
2. Upload the 4:3 cover and keep its returned URL as `cover43`.
3. Preupload the video through UPOS.
4. Upload all chunks with retry handling.
5. Finalize the UPOS upload.
6. Call `x/vu/web/add/v3` with both cover URLs.
7. Wait for review state and verify the public result.

## Temporary credentials

Prefer the extractor's temporary cookie file:

```bash
python3 scripts/publish_bilibili_dual_cover.py ...
```

When `--cookies` is supplied, read it but do not copy it into the repository.
Cookie JSON must never be committed, attached to an issue, included in a
screenshot, or written to a report.

## Verification

```bash
"$BILIBILI_PUBLISH_SKILL_DIR/scripts/verify_published.py" \
  --bvid "<bvid>" \
  --cookies "<temporary-cookies.json>"
```

Check all of the following:

- `view` returns `code=0`;
- `state=0`, or the submission is clearly still under review;
- a play URL exists;
- title, description, tags, and both covers match the approved metadata;
- the creator console has no rejection reason.

A temporary `-404` immediately after submission can mean the archive is still
being processed. Wait and re-check instead of submitting again.

## Recovery

- Cover failure: upload both variants again; do not publish with only one.
- Chunk failure: the publishing skill retries each chunk four times before
  giving up; preserve the preupload context if you resume manually.
- Mojibake: stop and validate the JSON as UTF-8 before resubmitting.
- Published content error: do not use the replace-source endpoint; create a
  new submission or hand the corrected file to the account owner.

## Cleanup

Delete temporary cookies after verification and close any Bilibili app
instance started solely for CDP extraction.

## Attribution

The publishing flow in `bilibili-publish` was refactored from
[sukai213/bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
(`skills/bilibili-ai-video`), which has no LICENSE file and states that its
skills and scripts are for personal learning and automation-workflow reference
only. See that repository's `THIRD_PARTY_NOTICES.md` for the full notice.
