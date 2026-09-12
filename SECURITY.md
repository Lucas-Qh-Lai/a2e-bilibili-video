# Security Policy

## Supported Versions

Security fixes are applied to the latest release on the default branch.

## Reporting a Vulnerability

Do not open a public issue for a credential leak, account takeover path, or
upload authorization bypass. Use GitHub's private vulnerability reporting
feature when available, or contact the maintainer through the repository
profile.

Include:

- affected version or commit;
- a minimal reproduction;
- impact;
- whether credentials or account data may have been exposed.

Do not include live cookies, tokens, or personal account information.

## Credential Rules

- Cookie files are temporary and must stay outside the repository.
- Never commit `.env`, `cookies.json`, API keys, or account exports.
- Do not paste secrets into issues, pull requests, logs, screenshots, or
  generated reports.
- Publishing requires explicit confirmation immediately before submission.
- Verify that temporary credentials are deleted after the workflow.

## Dependency Security

This repository invokes external projects at runtime. Review their licenses,
security posture, and release notes before use. Pinning and updating
dependencies is the responsibility of the operator.

