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

## Promotion candidate

Promotion `dev -> main` is distinct from implementation and from Architect contract acceptance.

After every repository mutation intended for the release is committed, including report/review artifacts when repository policy includes them, refresh `dev` and capture that exact SHA as `promotion_candidate_head`. Required authoritative verification must apply to **that exact SHA**.

Before promotion:

1. refresh exact `dev` and `main` HEADs;
2. require `dev` HEAD to still equal `promotion_candidate_head`;
3. confirm the candidate descends cleanly from the intended `main` under project policy and stop on unexpected divergence;
4. confirm required authoritative verification identifies the exact candidate SHA;
5. confirm no `dev` mutation occurred after that verification;
6. confirm explicit main-promotion authority;
7. promote exactly the verified candidate, preferring fast-forward semantics.

If `dev` changes after verification, the authorization is stale: `REVERIFY / REVIEW_REQUIRED`. A successful CI run for another SHA is not promotion evidence. Do not commit a “verification passed” artifact after verifying a candidate and then promote the new unverified HEAD.

Do not auto-promote after a successful push, review, or CI run.

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

For private repositories, standard GitHub-hosted runners consume the repository owner's included quota and may become billable after it is exhausted. Do not call a run free merely because it is short.

Git success, CI success, contract acceptance, Architect review, authoritative project PASS, promotion authorization, and actual promotion are separate signals.
