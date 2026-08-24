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

Refresh exact repository, branch, remote HEAD, expected base, write authority, and workflow triggers. If the remote branch moved, fail closed. Do not create extra branches or PRs merely by convention. Force-push and history rewrite are forbidden unless exceptional target governance explicitly requires them.

`task.git_authority` governs Executor Git mutations. Content ownership does not imply commit/push authority. `create_branch`, `commit`, `push`, and `promote_to_main` are independent capabilities. When `create_branch: false`, do not invoke branch creation even for tests or temporary work; use isolated fixtures for negative tests. Commit does not imply push, and push does not imply branch creation, force push, `main` mutation, or promotion.

## Promotion candidate lineage

Let `R = reviewed_report.commit` for the exact report accepted by Architect.

A valid `promotion_candidate_head` is only:

1. `R`; or
2. the single-parent direct child of `R`, whose only parent is `R`, with that single commit containing only the expected Architect-owned review artifact.

A merge commit or empty child is not the permitted review-artifact child. Any implementation, unrelated documentation, cleanup, dependency change, other task commit, unrelated commit, or second post-review commit after `R` invalidates accepted lineage and requires a new report plus Architect review.

Before promotion, refresh `dev` and `main`, require current `dev` equals the candidate, require authoritative verification to identify that exact SHA, and require explicit promotion authority. If `dev` changes after verification: `REVERIFY / REVIEW_REQUIRED`.

Do not auto-promote after push, review, CI, or verifier success.

## GitHub Actions

Prefer one bounded `push`-to-`dev` validation workflow with relevant paths, one standard Linux job, read-only contents, immutable action pins, concurrency cancellation, short timeout, validator plus stdlib unittests, and no manual dispatch, schedule, duplicate PR workflow, matrix, artifacts, cache, automatic rerun, larger runner, or paid external service.

Git success, CI success, Architect acceptance, authoritative project PASS, promotion authorization, and actual promotion remain separate signals.
