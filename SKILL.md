---
name: a2e-bilibili-video
description: Turn a topic or document into a researched explainer video with anything2explainer, render it at 1920x1080, create matching 16:9 and 4:3 covers through PPT Master, use Agent-selected Edge TTS, and publish the verified result to Bilibili. Use when the user asks for an explainer video plus Bilibili upload, A2E video publishing, or a topic-to-Bilibili production run.
---

# A2E Bilibili Video

An orchestration skill for producing an original explainer video and publishing
it to Bilibili:

- **Production:** `anything2explainer` (A2E)
- **Narration:** Edge TTS, with the voice selected by the Agent
- **Covers:** PPT Master, exported as independent 16:9 and 4:3 PNG files
- **Publishing:** the installed `bilibili-ai-video` skill and its CDP/UPOS flow

This repository does not vendor those upstream projects. It provides the
portable adapter, validation, documentation, and orchestration layer.

## Portable paths

Resolve the dependency roots before running commands:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export A2E_SKILL_DIR="${A2E_SKILL_DIR:-$CODEX_HOME/skills/anything2explainer}"
export BILIBILI_SKILL_DIR="${BILIBILI_SKILL_DIR:-$CODEX_HOME/skills/bilibili-ai-video}"
export PPT_MASTER_DIR="${PPT_MASTER_DIR:-$HOME/ppt-master/skills/ppt-master}"
export SKILL_DIR="${SKILL_DIR:-$CODEX_HOME/skills/a2e-bilibili-video}"
```

Run the dependency check first:

```bash
python3 "$SKILL_DIR/scripts/check_dependencies.py"
```

No machine-specific username, home directory, Codex checkout, or Bilibili
workspace path is embedded in this repository. Override the four variables
above when a dependency lives elsewhere.

## Fixed contracts

- **Delivery output defaults to 1920×1080, 30fps, H.264, AAC 44.1kHz.**
  A2E keeps its 1280×720 design coordinates for composition and QC. The final
  delivery render uses Remotion `--scale=1.5`; do not upscale a 720p render.
- **Use Edge TTS only.** The Agent chooses a voice from the Edge catalog and
  states the reason briefly before synthesis. Chinese defaults to Yunxi;
  English defaults to Andrew.
- **Create two independent covers:** `1920×1080` (16:9) and `1440×1080`
  (4:3). Both use the same visual language, but the 4:3 layout must be
  recomposed rather than produced by cropping the 16:9 cover.
- **Generate covers through PPT Master.** Use its Quick Generate path,
  validate the SVG roster, export an editable PPTX, and render both PNGs.
- **Stop for one final publish confirmation.** Show the video, both covers,
  title, description, tags, and partition before `add/v3` is called.
- **Never persist credentials.** Bilibili cookies stay in a temporary
  directory, are used only for extraction/upload/verification, and are deleted
  afterwards. Do not put cookies, API keys, or local paths in reports.

## Workflow

### 1. Produce the film with A2E

Read `$A2E_SKILL_DIR/SKILL.md` and execute its stages 0–8: research, narration,
timeline, storyboard, primitives, parallel construction, render, QC, and
delivery notes. Preserve A2E's four explicit user checkpoints.

Before A2E stage 2, select an Edge voice:

1. Chinese explainers and technical reviews: `zh-CN-YunxiNeural`.
2. Formal broadcast delivery: `zh-CN-YunyangNeural`.
3. Calm long-form narration: `zh-CN-YunjianNeural`.
4. English technical explainers: `en-US-AndrewNeural`.
5. Documentary authority: `en-US-ChristopherNeural`.
6. News delivery: `en-US-AriaNeural`.

Use `+8%` as the default Edge rate unless content density or an explicit user
request requires another value. Run A2E's TTS builder with
`TTS_ENGINE=edge` and the selected `VOICE`; do not fall back to Kokoro, Qwen3,
or MiMo.

### 2. Render the 1080p delivery master

The 720p A2E render is the QC and comparison pass. Produce the publish master
from the same project:

```bash
python3 "$SKILL_DIR/scripts/render_bilibili.py" \
  --project /absolute/path/to/a2e-project \
  --version v1
```

The script renders with Remotion `--scale=1.5`, converts the audio to AAC
44.1kHz, verifies the result with `ffprobe`, and writes:

```text
renders/<slug>_bilibili_v1.mp4
delivery/bilibili/<slug>_delivery.json
```

### 3. Build dual covers with PPT Master

Read [references/ppt-master-covers.md](references/ppt-master-covers.md). The
required outputs are:

```text
covers/<slug>_cover_16x9.svg
covers/<slug>_cover_16x9.png
covers/<slug>_cover_4x3.svg
covers/<slug>_cover_4x3.png
```

Use the registered `banner` canvas for 16:9. Use a custom `0 0 1440 1080`
canvas for 4:3. Keep the same title, proof points, palette, and visual
metaphor, but redesign the 4:3 composition.

When the PPT Master preview service is unavailable, render the SVGs with:

```bash
python3 "$SKILL_DIR/scripts/render_svg_cover.py" \
  --svg /path/to/cover_16x9.svg \
  --out /path/to/cover_16x9.png \
  --width 1920 --height 1080
```

### 4. Prepare Bilibili metadata

Read [references/bilibili-publish.md](references/bilibili-publish.md) and copy
[assets/publish.example.json](assets/publish.example.json) to a private project
file:

```json
{
  "title": "Title, at most 80 characters",
  "desc": "Description with a verified timeline and sources",
  "tag": "at most ten comma-separated tags",
  "dynamic": "Feed text",
  "tid": 231,
  "human_type2": 1012
}
```

Choose `tid` by subject. Common values are 231 (technology/computers), 95
(technology/digital), and 201 (knowledge/science).

### 5. Validate everything before publishing

```bash
python3 "$SKILL_DIR/scripts/validate_publish_assets.py" \
  --video /path/to/delivery.mp4 \
  --cover-16x9 /path/to/cover_16x9.png \
  --cover-4x3 /path/to/cover_4x3.png \
  --publish-json /path/to/publish.json
```

This checks resolution, frame rate, codecs, audio sample rate, cover ratios,
title/description limits, tag count, and UTF-8 metadata integrity.

### 6. Publish with both covers

After the final confirmation:

```bash
python3 "$SKILL_DIR/scripts/publish_bilibili_dual_cover.py" \
  --project /absolute/path/to/a2e-project \
  --video /path/to/delivery.mp4 \
  --cover-16x9 /path/to/cover_16x9.png \
  --cover-4x3 /path/to/cover_4x3.png \
  --config /path/to/publish.json
```

The adapter imports the installed `bilibili-ai-video` publishing functions;
it does not bundle or redistribute that project. It uploads both covers,
injects the 4:3 URL as `cover43`, and then verifies the public result.

If the Bilibili skill is installed elsewhere, pass
`--bilibili-skill-dir /absolute/path/to/bilibili-ai-video/scripts` or set
`BILIBILI_SKILL_DIR`.

## Verification

- A2E `selfcheck.py`, `motion_check.py`, and `frame_metrics.py` pass.
- The delivery master is 1920×1080, H.264, 30fps, AAC 44.1kHz.
- Both cover PNGs have exact dimensions and no clipped or missing text.
- `add/v3` receives both `cover` and `cover43`.
- Bilibili `view` returns `code=0`; review status has no rejection reason.
- Temporary cookies are deleted.

## References

- [PPT Master dual covers](references/ppt-master-covers.md)
- [Bilibili publishing and verification](references/bilibili-publish.md)
- [Architecture and boundaries](docs/architecture.md)

