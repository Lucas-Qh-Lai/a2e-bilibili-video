# Changelog

All notable changes are documented here.

## [0.1.4] - 2026-10-03

### Fixed

- **Path resolution in a shared-store layout.** The dependency check and the
  publishing adapter previously assumed `bilibili-publish` and
  `anything2explainer` live under `$CODEX_HOME/skills`. On a machine where the
  skills CLI manages them in the shared store, they live under
  `~/.agents/skills`, so both now search a candidate list:
  `$CODEX_HOME/skills`, `~/.agents/skills`, `~/.claude/skills`,
  `~/.config/opencode/skills`. An explicit
  `BILIBILI_PUBLISH_SKILL_DIR` / `A2E_SKILL_DIR` still wins.
- `bilibili-publish` no longer has to sit in `$CODEX_HOME/skills` for the
  adapter to find it.

## [0.1.3] - 2026-10-03

### Changed

- **Publishing now delegates to the standalone `bilibili-publish` skill.**
  The adapter no longer imports the upstream `bilibili-ai-video` publishing
  module; it validates the delivery assets and then invokes
  `bilibili-publish/scripts/publish_bilibili.py` through its command-line
  interface.
- The 4:3 cover is passed with `--cover43`, which `bilibili-publish` supports
  natively. The previous session-level shim that injected `cover43` into the
  `add/v3` payload has been removed.
- The dependency variable is now `BILIBILI_PUBLISH_SKILL_DIR`
  (default `$CODEX_HOME/skills/bilibili-publish`). `BILIBILI_SKILL_DIR` is
  still read as a fallback so existing setups keep working.
- Publishing receipts now record `published_by` so it is clear which skill
  performed the upload.

### Added

- `references/bilibili-publish.md` documents the CLI hand-off contract and
  retains the upstream attribution.

### Attribution

- The publishing flow in `bilibili-publish` was refactored from
  [sukai213/bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
  (`skills/bilibili-ai-video`). That repository has no LICENSE file and states
  that its skills and scripts are for personal learning and automation-workflow
  reference only. `bilibili-publish` rewrote the scripts and docs as an
  independent implementation and keeps a full notice in its own
  `THIRD_PARTY_NOTICES.md`; this repository neither copies nor redistributes
  either project's code.

## [0.1.2] - 2026-09-13

### First Stable Release

- This is the first installable and supported release of A2E Bilibili Video.
- The version remains `0.1.2` to preserve the project's continuous version
  history.

### Fixed

- Prefer the skill-local `.venv` when the publishing adapter runs its
  validator subprocess.
- Preserve virtual-environment context when resolving the Python executable.
  The previous implementation followed the `bin/python` symlink to the base
  interpreter and could lose access to project-local packages such as Pillow.

### Release Policy

- Future updates will use strictly increasing semantic versions.
- Previous releases and tags will be retained for historical traceability.

## [0.1.1] - 2026-09-13

### First Official Release

- Portable orchestration skill for the A2E explainer-video workflow.
- Agent-selected Edge TTS voice guidance for Chinese and English.
- 1920×1080 Remotion delivery rendering with AAC 44.1kHz output.
- Independent 16:9 and 4:3 PPT Master cover workflows.
- Bilibili dual-cover publishing with `cover` and `cover43`.
- Pre-publish video, cover, and metadata validation.
- Dependency checker and portable path resolution.
- Chinese-first README with an English companion and language switch.
- Human and Agent installation instructions.
- MIT license, third-party notices, security policy, contribution guide,
  changelog, issue templates, and CI validation.

### Fixed Before First Release

- Added the required skill entrypoint and reference documents.
- Made `--bilibili-skill-dir` accept the skill root directory consistently.
- Removed duplicated upstream submission logic from the cover adapter.
- Ensured the first release tag points to the complete installable revision.
