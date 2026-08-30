---
name: github-workflow
description: Use when target-authoritative Git/GitHub branch topology, commits, pushes, promotion, or GitHub Actions must be governed without inventing branches.
---

# GitHub Workflow

Repository-specific branch policy and exact live refs outrank generic defaults. This existing workflow owner supports three target-authoritative topologies:

- `MAIN_ONLY`: one working/stable `main`-style branch when target authority says so.
- `DEV_MAIN`: mutable `dev` integration plus stable `main`; this preserves backward compatibility for existing dev/main repositories.
- `DEV_STAGING_MAIN`: `dev` → `staging` → `main` only when explicitly activated by target authority.

Never infer or create staging merely because `DEV_STAGING_MAIN` is supported. Never create any branch from a generic topology default; branch creation always needs explicit target/task authority. Branch names and roles come from target authority, not this skill.

## Before writes

Refresh exact repository, target branch, remote HEAD, expected base, repository-specific branch policy, write authority, workflow triggers, and the semantic capabilities required for the current phase. Treat authorized remote Git state as canonical repository truth; local state is an execution copy. If the remote branch moved, that remote drift invalidates stale authority and fails closed. If a current-phase capability is unavailable, block before mutation. Do not require a later-phase capability to finish an earlier authorized phase.

A local clean/behind copy may be synchronized when authorized; local ahead or local dirty state is divergence or unknown work and must not be auto-pushed, reset, deleted, or silently adopted as authority.

`task.git_authority` governs Executor Git mutations. `create_branch`, `commit`, `push`, and promotion are independent. When `create_branch: false`, do not invoke branch creation even for tests or temporary work. Commit does not imply push, force push, stable-branch mutation, or promotion.

`release_authority` is separate again: `create_version_tag`, `mutate_repository_metadata`, and `publish_release` are independent permissions and are never inferred from commit, push, or promotion.

## Semantic capability preflight

Use phase-specific semantic requirements rather than equating authority with whichever API happens to exist. Route from required capability and evidence: resolve currently available candidates, reject candidates lacking current authority or sufficient evidence, then choose the lowest sufficient expected cost/resource burden. When materially equivalent, prefer fewer context transfers and lower consequence. Cheaper/free never permits weaker correctness, exact identity, acceptance evidence, safety, or required native/remote verification.

Availability, quota, rate limits, and paid capacity are runtime evidence. Installation, provider identity, historical availability, or an earlier preflight does not prove current availability after material environment/quota change. If the selected surface becomes unavailable or quota-limited, fallback may use only another currently available candidate that is already authorized and still sufficient for the same required capability/evidence; otherwise use an explicitly permitted degraded mode or fail closed with the existing capability/blocking semantics. Do not create provider/account rotation, quota-evasion, credential-broker, or persistent availability registries.

- `EXECUTION`: required repository content mutation and test/verification execution surfaces, including native verification when the task declares it mandatory for the current execution;
- `REVIEW`: exact commit/report resolution needed by the current governing Architect;
- `VERIFICATION`: designated authoritative exact-SHA verifier access;
- `PROMOTION`: non-force update of the authorized stable target ref to the exact candidate;
- `RELEASE`: only tag, repository-metadata, and release-publication capabilities for actions explicitly authorized.

Unavailable capability blocks only the current phase. For example, a successful promotion followed by missing release publication capability yields valid `PROMOTED_NOT_RELEASED` rather than invalidating promotion.

## Promotion candidate lineage

Let `R = reviewed_report.commit` for the exact report accepted by Architect.

A valid `promotion_candidate_head` is only:

1. `R`; or
2. the single-parent direct child of `R`, whose only parent is `R`, with that single commit containing only the expected Architect-owned review artifact.

A merge commit or empty child is not the permitted review-artifact child. Any implementation, unrelated documentation, cleanup, dependency change, other task commit, unrelated commit, or second post-review commit after `R` invalidates accepted lineage and requires a new report plus Architect review.

Canonical continuation does not derive a promotion branch from topology labels. Its `expected_refs` are zero or more explicit `{ref, commit}` identities, and canonical promotion uses `PROMOTE_TARGET_REF` plus `promotion_target_ref`; that target ref must be one of the expected refs so stale-target evidence is explicit. Existing expanded protocol-v3 `expected_refs.dev/main` plus `PROMOTE_TO_MAIN` remains compatibility input only and must not become the source of canonical branch-name assumptions.

Before promotion, refresh the candidate and the explicit promotion target ref, require the candidate ref equals the exact accepted candidate, require the target ref still equals its expected commit when that ref is part of the continuation snapshot, require authoritative verification to identify that exact SHA when required, require explicit promotion authority, and preflight promotion capability. If the candidate or required target ref changes after verification: `REVERIFY / REVIEW_REQUIRED`.

Do not auto-promote after push, review, CI, or verifier success. `AUTO_UNTIL_STOP` may only let orchestration dispatch an already-authorized promotion phase; it does not create promotion authority.

## Release lifecycle

After exact promotion, derive `PROMOTED_NOT_RELEASED` until all separately authorized release actions are complete. Tag creation, repository metadata mutation, and GitHub Release publication are independent actions. Missing authority or capability stops the release phase without rolling back the validity of the completed promotion.

`RELEASED` requires completed authorized release actions plus final exact identity/state verification. Promotion and release are never implied by a previous phase.

## GitHub Actions

For repositories that use `DEV_MAIN`, prefer one bounded push-to-integration validation workflow with relevant paths, one standard Linux job, read-only contents, immutable action pins, concurrency cancellation, short timeout, validator/tests, and no unnecessary dispatch, schedule, duplicate PR workflow, matrix, artifacts, cache, automatic rerun, larger runner, or paid external service. Other topologies use their target-authoritative integration/working branch rather than assuming `dev`.

Prefer one repository-owned deterministic verifier reused through whichever authorized surface is currently cheapest and sufficient. Local shell, Codex, Agent Runtime, and GitHub Actions should invoke the same verifier when feasible instead of carrying divergent verification logic. GitHub Actions is the bounded remote evidence boundary when exact task/target authority requires remote proof, not the default iterative debugger or mandatory development loop. ChatGPT+GitHub-only execution remains valid when no native-only capability is materially required.

Git success, CI success, Architect acceptance, authoritative project PASS, promotion authorization, actual promotion, release authorization, and actual release remain separate signals.
