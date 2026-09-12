# Bilibili Publishing and Verification

The adapter delegates publishing to a separately installed
`bilibili-ai-video` skill. The upstream project is not bundled or
redistributed by this repository.

## Dependencies

Resolve the upstream skill directory:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export BILIBILI_SKILL_DIR="${BILIBILI_SKILL_DIR:-$CODEX_HOME/skills/bilibili-ai-video}"
```

Expected files:

```text
$BILIBILI_SKILL_DIR/scripts/extract_bili_login_macos.sh
$BILIBILI_SKILL_DIR/scripts/publish_bilibili.py
$BILIBILI_SKILL_DIR/scripts/verify_published.py
```

On macOS, the extractor uses the logged-in Bilibili desktop app through CDP.
The app is restarted briefly with a debugging port. On other platforms,
provide an existing cookie JSON file with `--cookies`.

## Upload sequence

1. Upload the 16:9 cover and keep its returned URL as `cover`.
2. Upload the 4:3 cover and keep its returned URL as `cover43`.
3. Preupload the video through UPOS.
4. Upload all chunks with retry handling.
5. Finalize the UPOS upload.
6. Call `x/vu/web/add/v3` with both cover URLs.
7. Wait for review state and verify the public result.

The adapter uses the upstream skill's functions for steps 3–7. A narrow
session-level shim injects `cover43` into the `add/v3` payload because the
upstream helper currently defaults that field to an empty string.

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
"$BILIBILI_SKILL_DIR/scripts/verify_published.py" \
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
- Chunk failure: preserve the preupload context and follow the upstream retry
  behavior.
- Mojibake: stop and validate the JSON as UTF-8 before resubmitting.
- Published content error: do not use the replace-source endpoint; create a
  new submission or hand the corrected file to the account owner.

## Cleanup

Delete temporary cookies after verification and close any Bilibili app
instance started solely for CDP extraction.

