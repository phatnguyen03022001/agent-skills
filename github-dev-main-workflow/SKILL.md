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

Refresh exact repository, branch, remote HEAD, expected base, write authority, workflow triggers, and the semantic capabilities required for the current phase. Authorized remote Git state is canonical repository truth; local state is an execution copy. If the remote branch moved, that remote drift invalidates stale authority and fails closed. If a current-phase capability is unavailable, block before mutation. Do not require a later-phase capability to finish an earlier authorized phase.

A local clean/behind copy may be synchronized when authorized. Local ahead or local dirty state is divergence or unknown work and must not be auto-pushed, reset, deleted, or silently adopted as authority.

`task.git_authority` governs Executor Git mutations. `create_branch`, `commit`, `push`, and `promote_to_main` are independent. When `create_branch: false`, do not invoke branch creation even for tests or temporary work. Commit does not imply push, force push, `main` mutation, or promotion.

`release_authority` is separate again: `create_version_tag`, `mutate_repository_metadata`, and `publish_release` are independent permissions and are never inferred from commit, push, or `promote_to_main`.

## Semantic capability preflight

Use phase-specific semantic requirements rather than equating authority with whichever API happens to exist. A known capability is not proof of a currently available capability. Choose the least-powerful currently available surface sufficient for the phase and use bounded escalation only when required.

- `EXECUTION`: required repository content mutation and test/verification execution surfaces, including native verification when the task declares it mandatory for the current execution;
- `REVIEW`: exact commit/report resolution needed by the independent Architect/session;
- `VERIFICATION`: authoritative exact-SHA verifier access;
- `PROMOTION`: non-force update of the authorized `main` ref to the exact candidate;
- `RELEASE`: only the tag, repository-metadata, and release-publication capabilities for actions explicitly authorized.

Unavailable capability blocks only the current phase. For example, a successful promotion followed by missing release publication capability yields valid `PROMOTED_NOT_RELEASED` rather than invalidating promotion.

## Promotion candidate lineage

Let `R = reviewed_report.commit` for the exact report accepted by Architect.

A valid `promotion_candidate_head` is only:

1. `R`; or
2. the single-parent direct child of `R`, whose only parent is `R`, with that single commit containing only the expected Architect-owned review artifact.

A merge commit or empty child is not the permitted review-artifact child. Any implementation, unrelated documentation, cleanup, dependency change, other task commit, unrelated commit, or second post-review commit after `R` invalidates accepted lineage and requires a new report plus Architect review.

Before promotion, refresh `dev` and `main`, require current `dev` equals the candidate, require authoritative verification to identify that exact SHA when required, require explicit promotion authority, and preflight promotion capability. If `dev` changes after verification: `REVERIFY / REVIEW_REQUIRED`.

Do not auto-promote after push, review, CI, or verifier success. `AUTO_UNTIL_STOP` may only let orchestration dispatch an already-authorized promotion phase; it does not create promotion authority.

## Release lifecycle

After exact promotion, derive `PROMOTED_NOT_RELEASED` until all separately authorized release actions are complete. Tag creation, repository metadata mutation, and GitHub Release publication are independent actions. Missing authority or capability stops the release phase without rolling back the validity of the completed promotion.

`RELEASED` requires completed authorized release actions plus final exact identity/state verification. Promotion and release are never implied by a previous phase.

## GitHub Actions

Prefer one bounded `push`-to-`dev` validation workflow with relevant paths, one standard Linux job, read-only contents, immutable action pins, concurrency cancellation, short timeout, validator plus stdlib unittests, and no manual dispatch, schedule, duplicate PR workflow, matrix, artifacts, cache, automatic rerun, larger runner, or paid external service.

Git success, CI success, Architect acceptance, authoritative project PASS, promotion authorization, actual promotion, release authorization, and actual release remain separate signals.
