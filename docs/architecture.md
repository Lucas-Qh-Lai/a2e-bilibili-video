# Architecture

## Design Goal

Keep the production, cover-design, and publishing systems separate while
providing one predictable entrypoint.

```text
topic or document
        |
        v
anything2explainer
  research -> narration -> timeline -> storyboard -> shots -> QC
        |
        +--> Edge TTS voiceover
        |
        v
Remotion 1920x1080 delivery render
        |
        +----------------------------+
        |                            |
        v                            v
PPT Master 16:9 cover        PPT Master 4:3 cover
        |                            |
        +-------------+--------------+
                      v
          asset and metadata validation
                      v
          bilibili-ai-video publishing
             cover + cover43 + UPOS
                      v
               public verification
```

## Ownership Boundaries

| Component | Owns | Does not own |
|---|---|---|
| `anything2explainer` | Research, script, timeline, storyboard, shots, QC | Bilibili metadata |
| Edge TTS | Voice synthesis | Video rendering |
| Remotion | Final frame rendering | Presentation editing |
| PPT Master | Cover design and editable PPTX | Main video animation |
| `bilibili-ai-video` | Login, UPOS, upload, verification | Video production |
| This repository | Integration, portability, validation | Upstream source code |

## Why Not Merge the Projects

The three upstream systems have different canonical artifacts:

- A2E's canonical artifact is a frame-accurate Remotion composition.
- PPT Master's canonical artifact is an editable PPTX.
- The Bilibili skill's canonical artifact is a published archive and its
  verification state.

Merging them would create conflicting renderers, timing models, preview
systems, and quality gates. This repository instead defines narrow interfaces:

1. A2E produces a project and a 1280×720 QC render.
2. The adapter renders the same project at 1920×1080.
3. PPT Master produces two cover PNGs and source SVGs.
4. Validation checks the final file contract.
5. The publishing adapter delegates to the installed Bilibili skill.

## Path Resolution

No user-specific path is committed.

| Variable | Default |
|---|---|
| `CODEX_HOME` | `$HOME/.codex` |
| `A2E_SKILL_DIR` | `$CODEX_HOME/skills/anything2explainer` |
| `BILIBILI_SKILL_DIR` | `$CODEX_HOME/skills/bilibili-ai-video` |
| `PPT_MASTER_DIR` | `$HOME/ppt-master/skills/ppt-master` |
| `CHROME_PATH` | Auto-detected or omitted |

## Trust Boundaries

- Upstream projects are cloned or installed by the user.
- This repository imports the upstream publishing module at runtime.
- Cover and video files are validated before any upload.
- The publishing adapter requires explicit user confirmation upstream of the
  tool call.
- Cookie material is never written into the repository or logs.

