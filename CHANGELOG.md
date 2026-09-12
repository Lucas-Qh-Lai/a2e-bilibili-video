# Changelog

All notable changes are documented here.

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
