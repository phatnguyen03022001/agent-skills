---
name: github-dev-main-workflow
description: Use when a repository follows a dev/main branch model and a task may read or write GitHub state, commit, push, promote changes, create refs, or trigger GitHub Actions.
---

# GitHub Dev/Main Workflow

## Branch invariant

Use exactly two default long-lived branches:

- `dev`: integration and normal mutation target.
- `main`: stable source of truth.

Do not create additional branches or PRs unless the user or repository governance explicitly requires them. Do not implement directly on `main`. Promotion from `dev` to `main` is a separate authorized operation.

## Before any write

Confirm from live GitHub/Git state:

1. exact `owner/repo`;
2. exact target branch;
3. current remote HEAD;
4. expected base HEAD;
5. scope and write authority;
6. whether the write can trigger GitHub Actions or other paid infrastructure.

Never rely on folder names, old conversation state, or a previously observed SHA.

If remote state moved, stop and reassess. Normal updates must be fast-forward safe. No force-push, history rewrite, destructive reset of unknown user work, or silent conflict resolution.

A new chat must not mutate a repository until repository + branch + exact base HEAD are explicit.

## Write policy

Normal implementation writes target `dev`. Read the current file/blob before replacing it. Keep commits atomic and task-scoped. Commit and push only when authorized.

Promotion to `main` requires:

- exact `dev` and `main` heads refreshed;
- required project verification satisfied on the intended SHA;
- explicit promotion authority;
- no unexpected divergence.

Third-party or delegated workers should receive `dev` mutation authority only unless explicitly trusted for promotion.

## Actions and cost

Before push, merge, rerun, or dispatch, inspect applicable workflow triggers, runner types, matrices, caches/artifacts, and expected job fan-out when available.

Do not create, broaden, rerun, or dispatch GitHub Actions merely for convenience. Do not enable paid GitHub features, larger runners, extra storage, or unknown-cost compute without explicit approval.

When cost matters, verify current GitHub billing rules. A short run is not proof of free usage. Prefer repository-native/local verification when it provides the required evidence and project governance allows it.

Cost optimization must never weaken required correctness.

## Verification separation

Keep distinct: Git write success, local checks, Actions checks, contract compliance, and authoritative project verification. A successful push is not project PASS.

Fail closed on wrong repo, wrong branch, stale base, unclear scope/write authority, unexpected remote movement, unapproved main promotion, potentially paid execution without approval, or required verification failure.
