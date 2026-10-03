# Third-Party Notices

This repository integrates with, but does not bundle:

## anything2explainer

- Repository: https://github.com/Vincentwei1021/anything2explainer
- Author: Vincent Wei
- Role: explainer-video production workflow and Remotion template
- License: PolyForm Noncommercial 1.0.0, as declared by the upstream project

Users are responsible for reviewing and complying with the upstream license,
especially for commercial use.

## PPT Master

- Repository: https://github.com/hugohe3/ppt-master
- Author: Hugo He
- Role: presentation and cover design workflow
- License: MIT

## bilibili-publish

- Repository: https://github.com/Lucas-Qh-Lai/bilibili-publish
- Author: Lucas-Qh-Lai
- Role: publishing skill invoked at runtime by this repository's adapter
- License: MIT (for that repository's own code)

This repository does not copy or redistribute `bilibili-publish`. It invokes
that skill's command-line entry point at runtime from the user's local
installation.

## bilibili-ai-skills

- Repository: https://github.com/sukai213/bilibili-ai-skills
- Author: sukai213
- Role: original source of the Bilibili publishing flow (upstream of
  `bilibili-publish`)
- License: no LICENSE file; the project's README states that its skills and
  scripts are for personal learning and automation-workflow reference only

The publishing flow in `bilibili-publish` was refactored from this project.
`bilibili-publish` rewrote the scripts and documentation as an independent
implementation and keeps a full attribution notice in its own
`THIRD_PARTY_NOTICES.md`. This repository neither copies nor redistributes
either project's source code.

## Runtime Dependencies

This repository may invoke:

- Node.js and npx
- Remotion
- Edge TTS
- FFmpeg and ffprobe
- Python packages listed in `scripts/requirements.txt`
- a Chromium-based browser for optional SVG-to-PNG rendering

Each dependency is governed by its own license.
