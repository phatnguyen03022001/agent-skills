---
name: security-review
description: Use when a change affects authentication, authorization, secrets, sensitive data, trust boundaries, untrusted input, external integrations, dependencies, or other security-critical behavior.
---

# Security Review

Review security as a design property with concrete threat paths, not as a generic checklist.

## Model the system

Identify protected assets, actors, entry points, trust boundaries, data flows, privileges, external dependencies, and security assumptions. Read the target repository’s security policy and existing controls before proposing new ones.

Ask what an attacker or compromised dependency can influence and what authority each component actually needs.

## Analyze threats and controls

Focus where relevant on:

- authentication, session/token lifecycle, and identity binding;
- authorization at the resource/action boundary, including tenant isolation;
- validation and canonicalization of untrusted input;
- injection and unsafe interpretation;
- secrets, keys, credentials, and logging exposure;
- sensitive-data collection, storage, transit, retention, and deletion;
- SSRF/path traversal/file or URL handling;
- dependency and supply-chain trust;
- webhook/signature/replay semantics;
- privilege escalation and confused-deputy paths;
- secure defaults, least privilege, and failure behavior.

Trace concrete attack paths from controllable source to meaningful sink. Distinguish a plausible vulnerability from a scanner-shaped suspicion. When safe and authorized, validate findings with minimal reproducible evidence rather than inflating severity from theory.

## Prioritize

Rank findings by exploitability, impact, exposure, and existing mitigations. Recommend the smallest control that closes the threat without breaking product constraints. Prefer standard, well-maintained security mechanisms over custom cryptography or bespoke identity systems.

Security controls still require verification. Specify negative and boundary tests when they materially prove the control.

Treat security findings skeptically in both directions. Do not dismiss a path because exploitation seems inconvenient, and do not promote a theoretical pattern to critical severity without showing how attacker-controlled data reaches a privileged effect. Record prerequisites and existing mitigations explicitly. For version-sensitive controls or vulnerabilities, verify current upstream guidance rather than relying on remembered best practices.

## Boundaries

Use `adversarial-audit` for non-malicious fault pressure and governance bypasses, `reuse-first` for selecting established security mechanisms, and `reliability` for availability/recovery concerns.

Do not broaden scope into a repository-wide security audit unless authorized, and do not claim a project secure because one change passed review.
