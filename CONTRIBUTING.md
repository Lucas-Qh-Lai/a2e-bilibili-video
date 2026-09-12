# Contributing

## Scope

Contributions should improve the integration layer, portability, validation,
documentation, or tests. Do not vendor upstream projects into this repository
without checking their licenses first.

## Development

1. Fork the repository.
2. Create a focused branch.
3. Install the local Python dependencies:

   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install -r scripts/requirements.txt
   ```

4. Run syntax and dependency checks:

   ```bash
   python -m compileall -q scripts
   python scripts/check_dependencies.py
   ```

5. Keep changes portable. Do not add absolute paths, usernames, cookies,
   tokens, or machine-specific assumptions.

## Pull Requests

Include:

- the problem being solved;
- the behavior change;
- the verification performed;
- any upstream compatibility risk.

For publishing changes, explain how the change was tested without exposing
credentials or uploading an unintended public video.

## Commit Style

Use concise Conventional Commit-style messages where practical, for example:

```text
fix: validate cover43 dimensions before upload
docs: clarify Agent installation flow
```

## Licensing

By contributing, you agree that your contribution may be distributed under
the repository's MIT License. Do not submit code copied from an upstream
project unless its license permits redistribution and the source is credited.

