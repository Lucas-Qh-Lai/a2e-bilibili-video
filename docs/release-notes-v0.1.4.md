# v0.1.4 — Locating the publishing skill in a shared store

## What changed

A fix for machines where the `skills` CLI manages skills in the shared
cross-agent store rather than in `$CODEX_HOME/skills`.

- The dependency check and the publishing adapter now search a candidate list
  instead of assuming a single directory:

  ```text
  $CODEX_HOME/skills/<name>
  ~/.agents/skills/<name>
  ~/.claude/skills/<name>
  ~/.config/opencode/skills/<name>
  ```

- An explicit `BILIBILI_PUBLISH_SKILL_DIR` or `BILIBILI_SKILL_DIR` still takes
  precedence, and `A2E_SKILL_DIR` still overrides the `anything2explainer`
  location.
- `bilibili-publish` no longer has to be installed under `$CODEX_HOME/skills`
  for the adapter to find it.

## Why

On this setup the `skills` CLI installs into `~/.agents/skills`, and other
agent directories reference that store (`~/.claude/skills` is a symlink to it,
and OpenCode links into it). Hard-coding `$CODEX_HOME/skills` made publishing
fail once the redundant `$CODEX_HOME/skills` copies were removed.

## Verification

```bash
python3 scripts/check_dependencies.py
```

All three external dependencies should report `OK`:

```text
A2E              OK   ~/.agents/skills/anything2explainer
Bilibili publish OK   ~/.agents/skills/bilibili-publish
PPT Master       OK   ~/ppt-master/skills/ppt-master
```

## Release Policy

Future updates use strictly increasing semantic versions. Previous releases and
tags are retained.
