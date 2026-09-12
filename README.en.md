# A2E Bilibili Video

[English](README.en.md) | [简体中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-000000)](https://openai.com/codex)
[![Remotion](https://img.shields.io/badge/Remotion-4.x-0B84F3)](https://www.remotion.dev/)
[![Edge TTS](https://img.shields.io/badge/TTS-Edge%20TTS-0078D4)](https://github.com/rany2/edge-tts)
[![Bilibili](https://img.shields.io/badge/Publish-Bilibili-00A1D6)](https://www.bilibili.com/)

Turn a topic, article, or document into an original code-animated explainer
video, create matching 16:9 and 4:3 covers, and publish the verified result to
Bilibili.

This project is an orchestration skill. It connects three existing projects
instead of replacing them:

- [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
  provides the production workflow and Remotion template.
- [ppt-master](https://github.com/hugohe3/ppt-master) provides the cover
  design workflow and editable PPTX output.
- [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
  provides the Bilibili publishing flow.

The repository contains only the integration layer, portable scripts,
validators, and documentation. It does not vendor upstream source code,
credentials, generated videos, or machine-specific paths.

## What It Does

| Stage | Result |
|---|---|
| Research and script | Sourced research notes, narration, storyboard, and shot plan |
| Voiceover | Edge TTS with an Agent-selected voice |
| Motion graphics | Remotion scenes rendered at 1920×1080 |
| Quality control | Static checks, motion checks, frame metrics, and visual review |
| Covers | Independent 1920×1080 and 1440×1080 PPT Master covers |
| Publishing | CDP login extraction, dual-cover upload, `add/v3`, and verification |

## Requirements

### Required software

- Node.js 18 or newer, plus `npx`
- Python 3.10 or newer
- `ffmpeg` and `ffprobe`
- Git
- A Codex installation with skill support

### Required upstream skills

Install these separately:

1. [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
2. [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
3. [ppt-master](https://github.com/hugohe3/ppt-master)

### Platform notes

- macOS is the primary publishing platform because the bundled Bilibili
  flow uses the logged-in Bilibili desktop app through CDP.
- Remotion rendering and PPT Master cover generation can run on other
  platforms when their dependencies are available.
- Automatic PowerPoint video export is not used by this skill. Remotion owns
  the final video render.

## Installation

Choose the path that matches how you use Codex.

### For humans

#### 1. Install the command-line dependencies

macOS:

```bash
brew install node ffmpeg
```

Ubuntu or Debian:

```bash
sudo apt update
sudo apt install nodejs npm ffmpeg
```

Verify:

```bash
node --version
npx --version
ffmpeg -version
ffprobe -version
python3 --version
```

#### 2. Install the three upstream skills

Install `anything2explainer` into the Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/Vincentwei1021/anything2explainer.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/anything2explainer"
```

Install the Bilibili skill:

```bash
git clone https://github.com/sukai213/bilibili-ai-skills.git /tmp/bilibili-ai-skills
cp -R /tmp/bilibili-ai-skills/skills/bilibili-ai-video \
  "${CODEX_HOME:-$HOME/.codex}/skills/bilibili-ai-video"
```

Install PPT Master:

```bash
git clone https://github.com/hugohe3/ppt-master.git "$HOME/ppt-master"
```

If any project is installed elsewhere, set `A2E_SKILL_DIR`,
`BILIBILI_SKILL_DIR`, and `PPT_MASTER_DIR`. No script assumes a username or
home directory.

#### 3. Install this integration skill

```bash
git clone https://github.com/Lucas-Qh-Lai/a2e-bilibili-video.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/a2e-bilibili-video"
```

#### 4. Install Python dependencies

Use a project-local virtual environment:

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/a2e-bilibili-video"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

PPT Master may have its own Python dependencies. Follow its installation
guide instead of installing PPT Master packages globally.

#### 5. Verify the installation

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export A2E_SKILL_DIR="$CODEX_HOME/skills/anything2explainer"
export BILIBILI_SKILL_DIR="$CODEX_HOME/skills/bilibili-ai-video"
export PPT_MASTER_DIR="$HOME/ppt-master/skills/ppt-master"

python3 scripts/check_dependencies.py
```

All required checks should report `OK`. Restart Codex after installation so
the new skill appears in the skill index.

### For Agents

An Agent should perform these steps deterministically:

1. Detect the operating system and verify `git`, `node`, `npx`, `ffmpeg`,
   `ffprobe`, and Python are available.
2. Resolve `CODEX_HOME` from the environment, defaulting to `$HOME/.codex`.
3. Clone or update `anything2explainer` to
   `$CODEX_HOME/skills/anything2explainer`.
4. Clone or update `bilibili-ai-skills`, then install only its
   `skills/bilibili-ai-video` directory to
   `$CODEX_HOME/skills/bilibili-ai-video`.
5. Install `ppt-master` to `$HOME/ppt-master` unless the user provides a
   path.
6. Install this repository to `$CODEX_HOME/skills/a2e-bilibili-video`.
7. Create a project-local Python virtual environment and install
   `scripts/requirements.txt`.
8. Export `A2E_SKILL_DIR`, `BILIBILI_SKILL_DIR`, and `PPT_MASTER_DIR` for the
   current command.
9. Run `scripts/check_dependencies.py` and report each failure separately.
10. Never copy, print, or commit cookies, tokens, API keys, or local account
    data.

Do not modify an existing local skill unless the user explicitly asks for it.

## Quick Start

Set the dependency roots:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export A2E_SKILL_DIR="$CODEX_HOME/skills/anything2explainer"
export BILIBILI_SKILL_DIR="$CODEX_HOME/skills/bilibili-ai-video"
export PPT_MASTER_DIR="$HOME/ppt-master/skills/ppt-master"
export SKILL_DIR="$CODEX_HOME/skills/a2e-bilibili-video"
```

Ask Codex:

```text
Use a2e-bilibili-video to turn this topic into a 4-minute Chinese explainer
video, create both Bilibili covers, and publish it after showing me the final
metadata for approval.
```

The skill follows the A2E workflow, selects an Edge voice, creates both
cover variants, validates the delivery assets, waits for final approval, and
then publishes both covers.

## Output Contract

```text
renders/<slug>_bilibili_v1.mp4
delivery/bilibili/<slug>_delivery.json
covers/<slug>_cover_16x9.png
covers/<slug>_cover_4x3.png
covers/<slug>_cover_16x9.svg
covers/<slug>_cover_4x3.svg
delivery/bilibili/publish_result.json
```

The final video is 1920×1080, 30fps, H.264, AAC 44.1kHz. A2E's 1280×720
canvas is a design coordinate system, not the delivery resolution.

## Repository Layout

```text
.
├── SKILL.md
├── agents/openai.yaml
├── assets/publish.example.json
├── docs/architecture.md
├── references/bilibili-publish.md
├── references/ppt-master-covers.md
├── scripts/check_dependencies.py
├── scripts/publish_bilibili_dual_cover.py
├── scripts/render_bilibili.py
├── scripts/render_svg_cover.py
├── scripts/validate_publish_assets.py
└── scripts/requirements.txt
```

## Privacy and Security

- No credentials are stored in this repository.
- Cookie JSON is temporary and must remain outside version control.
- `.gitignore` excludes `.env`, cookie files, keys, generated media, and
  project workspaces.
- Reports and issue templates must not request secrets.
- Publishing requires explicit human confirmation immediately before the
  `add/v3` call.

See [SECURITY.md](SECURITY.md).

## Limitations

- Bilibili upload depends on the external skill and the Bilibili API.
- CDP extraction currently assumes macOS and the Bilibili desktop app.
- PPT Master's native PowerPoint video export is not used; Remotion renders
  the final video.
- The upstream projects have their own licenses and must be installed
  separately.
- Generated videos and covers are user artifacts and are not distributed
  with this repository.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Credits

### Upstream Projects

This project depends on and thanks:

1. [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
   for the production workflow, Remotion template, motion language, and QC
   system.
2. [ppt-master](https://github.com/hugohe3/ppt-master) for the presentation
   and cover design workflow.
3. [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills) for
   the Bilibili publishing and verification flow.

Their authors retain all rights to their work.

### Co-creators

- **OpenAI Codex**
- **DeepSeek V4.1 Flash**

This integration layer was developed through an Agent-assisted workflow
involving both systems.

## License

The integration layer in this repository is licensed under the
[MIT License](LICENSE). Upstream projects remain under their own licenses.

## Roadmap

- Cross-platform Bilibili cookie extraction
- More cover templates and layout presets
- Optional subtitle export
- More publish validators
- Additional platform adapters

