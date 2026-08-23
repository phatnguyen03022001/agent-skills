---
name: github-dev-main-workflow
description: Use when a repository uses a dev integration branch and main stable branch and work may read or mutate Git state, commit, push, promote, or trigger GitHub Actions.
---

# GitHub Dev/Main Workflow

Use a two-branch authority model:

- `dev` = integration and normal mutation branch.
- `main` = stable, authoritative branch.

Target-repository governance may be stricter and takes precedence.

## Before writes

Refresh and verify exact `owner/repo`, target branch, remote HEAD, expected base HEAD, write authority, and relevant workflow triggers. Read current files/blobs before replacement.

A fresh execution chat must not mutate without exact repository + branch + base HEAD. If the remote branch moved, fail closed and require review/re-contracting. Never silently reset, rebase, or discard unknown work.

Normal implementation and delegated-agent writes default to `dev`. Do not create extra branches or PRs merely by convention. Force-push and history rewrite are forbidden unless exceptional target governance explicitly requires them.

## Promotion

Promotion `dev -> main` is distinct from implementation. Before promotion:

1. refresh exact `dev` and `main` HEADs;
2. stop on unexpected divergence;
3. confirm required verification passed on the intended `dev` SHA;
4. confirm explicit main-promotion authority;
5. prefer fast-forward semantics when history permits.

Do not auto-promote after a successful push or CI run.

## GitHub Actions

Actions on `dev` can be useful, but inspect cost/fan-out before push, rerun, dispatch, or workflow changes.

Prefer bounded validation:

- relevant `push` to `dev`;
- one standard Linux job when practical;
- no matrix unless required;
- no duplicate push + PR validation;
- no schedule or automatic reruns without a real need;
- no artifacts/cache unless they materially help;
- concurrency cancellation and short timeouts when appropriate;
- no larger runners or external paid services by convenience.

For private repositories, standard GitHub-hosted runners consume the repository owner's included quota and may become billable after it is exhausted. Do not call a run free merely because it is short. Check current GitHub billing rules when cost matters.

Local verification can reduce unnecessary remote runs, but cost optimization must not weaken required correctness.

Git success, CI success, contract compliance, Architect review, and authoritative project PASS are separate signals.
