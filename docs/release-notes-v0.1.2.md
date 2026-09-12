# A2E Bilibili Video v0.1.2

**First official release.** This is the first installable and supported version
of the A2E Bilibili Video skill.

The version number is `0.1.2` because the repository retains its continuous
version history. Functionally, this is the first stable release that users
should install.

## Summary

A2E Bilibili Video is a portable Codex skill that connects three existing
projects into one explainer-video production and publishing workflow:

- **anything2explainer** for research, narration, storyboard, Remotion motion
  graphics, and frame-level quality control.
- **PPT Master** for designing the 16:9 and 4:3 covers and exporting editable
  source files.
- **bilibili-ai-skills** for Bilibili login, UPOS upload, submission, and
  post-publish verification.

The integration layer is licensed under MIT and does not redistribute upstream
source code, credentials, generated media, or machine-specific paths.

## What Is Included

### End-to-End Workflow

- Uses the A2E production flow from topic or source document to final video.
- Keeps A2E's research, script approval, storyboard, parallel build, render,
  QC, and delivery stages.
- Adds one final publication confirmation before the Bilibili submission is
  created.

### Edge TTS

- Uses Edge TTS only for generated narration.
- Lets the Agent select a voice based on language, content type, and tone.
- Includes Chinese and English voice guidance.
- Uses `+8%` as the default speaking rate unless the content requires a
  different pace.

### 1920×1080 Delivery Rendering

- Keeps A2E's 1280×720 design coordinates for composition and QC.
- Renders the delivery master with Remotion `--scale=1.5`.
- Produces a true 1920×1080 H.264 video instead of stretching a 720p render.
- Converts the delivery audio to AAC 44.1kHz.
- Verifies resolution, frame rate, codecs, audio sample rate, and output
  existence before reporting success.
- Writes a delivery receipt beside the rendered master.

### Dual PPT Master Covers

- Produces an independent 1920×1080 16:9 main cover.
- Produces an independent 1440×1080 4:3 secondary cover.
- Uses the same title, proof points, palette, and visual metaphor while
  recomposing the 4:3 layout instead of cropping the 16:9 version.
- Supports PPT Master's normal SVG validation and editable PPTX export.
- Includes a portable SVG-to-PNG renderer for environments where the PPT
  Master preview server is unavailable.

### Bilibili Publishing

- Uploads the 16:9 cover as `cover`.
- Uploads the 4:3 cover as `cover43`.
- Uses the installed `bilibili-ai-video` skill for CDP login extraction,
  UPOS preupload, chunk upload, finalization, `add/v3`, and verification.
- Injects `cover43` at the HTTP session boundary instead of duplicating the
  upstream publishing implementation.
- Supports an explicit cookie file for non-macOS environments.
- Deletes temporary credentials after the run.

### Validation and Safety

- Validates video dimensions, frame rate, H.264 video, AAC audio, and 44.1kHz
  sample rate.
- Validates exact cover dimensions.
- Validates title length, description length, tag count, and JSON integrity.
- Rejects obvious mojibake before submission.
- Keeps cookies, tokens, API keys, local account data, and generated media out
  of version control.
- Requires explicit human confirmation before the public submission call.

### Local Runtime Integration

- Prefers the skill-local `.venv` when the publishing adapter launches its
  validator subprocess.
- Preserves virtual-environment context instead of resolving `bin/python` to
  the base interpreter.
- Keeps validator dependencies such as Pillow available even when the parent
  process was started from a uv-managed Python runtime.
- Uses portable environment variables for the three upstream dependency
  roots.

## Installation

The README includes two separate installation paths:

- **Human installation:** command-line prerequisites, upstream clones, Python
  environment, dependency verification, and Codex restart.
- **Agent installation:** deterministic steps for resolving `CODEX_HOME`,
  installing all three upstream skills, creating the local environment, and
  reporting dependency failures.

See:

- [Chinese README](https://github.com/Lucas-Qh-Lai/a2e-bilibili-video/blob/main/README.md)
- [English README](https://github.com/Lucas-Qh-Lai/a2e-bilibili-video/blob/main/README.en.md)

## Upstream Dependencies

This release requires these original projects to be installed separately:

1. [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
2. [ppt-master](https://github.com/hugohe3/ppt-master)
3. [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)

The upstream projects retain their own licenses. In particular, users should
review anything2explainer's PolyForm Noncommercial terms before commercial use.
This integration repository does not redistribute the Bilibili skill.

## Portable Paths

No username, home directory, Codex checkout, or Bilibili workspace path is
embedded in the repository.

The scripts resolve dependencies through:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export A2E_SKILL_DIR="${A2E_SKILL_DIR:-$CODEX_HOME/skills/anything2explainer}"
export BILIBILI_SKILL_DIR="${BILIBILI_SKILL_DIR:-$CODEX_HOME/skills/bilibili-ai-video}"
export PPT_MASTER_DIR="${PPT_MASTER_DIR:-$HOME/ppt-master/skills/ppt-master}"
export SKILL_DIR="${SKILL_DIR:-$CODEX_HOME/skills/a2e-bilibili-video}"
```

Run the dependency checker after installation:

```bash
python3 "$SKILL_DIR/scripts/check_dependencies.py"
```

## Verification

Before release:

- Python scripts compile successfully.
- The required skill structure is present.
- The README, English README, MIT license, changelog, and third-party notices
  are present.
- The public GitHub workflow passes.
- The Bilibili `cover43` injection is covered by a local mock test.
- The release tag points to the current published commit.
- The local migrated installation passes the dependency check.
- The local publishing adapter validates a test video and both cover ratios.
- The 1920×1080 Remotion render path produces H.264 video with AAC 44.1kHz.

## Privacy

The public repository contains no:

- Bilibili cookies;
- API keys or access tokens;
- `.env` files;
- local account exports;
- machine usernames or home-directory paths;
- generated videos or private project workspaces.

## Licensing

This integration layer is released under the MIT License.

Upstream projects are not covered by this license and must be installed and
used under their own terms.

## Credits

### Upstream Projects

- [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
- [PPT Master](https://github.com/hugohe3/ppt-master)
- [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)

### Co-creators

- **OpenAI Codex**
- **DeepSeek V4.1 Flash**

## First-Release Scope

This is a focused integration release. It does not vendor the upstream
projects, provide a hosted service, or guarantee that Bilibili API behavior
will remain unchanged. Cross-platform cookie extraction, additional cover
presets, optional subtitle export, and more validators are planned for future
releases.

## Release Policy

- Future updates will use monotonically increasing semantic versions.
- Existing releases and tags will be retained.
- New releases will add to the project history instead of replacing or
  deleting an earlier release.
- Patch releases fix compatibility or correctness.
- Minor releases add capabilities without breaking the documented workflow.
- Major releases are reserved for incompatible interface or workflow changes.
