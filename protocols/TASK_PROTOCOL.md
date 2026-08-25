# Task Protocol

This protocol defines reusable Architect-to-Executor governance across repositories. `agent-skills` owns how work is governed; each target repository owns what its product is and stores its live tasks.

Supported protocol version: **3**. These additions are backward-compatible. Existing valid expanded v3 artifacts remain valid; optional controls that are absent default to manual, fail-closed, and non-permissive behavior. Unsupported versions fail closed and are never silently upgraded.

## Core bindings

An Architect session binds to one immutable target repository. External repositories and documentation may be read as references but never become implicit targets. Asking the bound Architect to govern a different target produces `NEW_ARCHITECT_SESSION_REQUIRED`.

An Executor session binds to one approved task revision, one repository, one branch, and one exact execution authorization. It does not execute unrelated work, reinterpret architecture, or broaden scope. The approved exact task plus handoff is prior authorization for its bounded Executor actions; a role must not invent extra user approvals for phases already authorized by those artifacts.

## Architect judgment and material user decisions

Architect optimizes for the user's durable user objective and explicit current product/design authority. Canonical authority is governing, not infallible: derived architecture, implementation accident, reviewer preference, or even current canonical text may be challenged only with concrete evidence of staleness, contradiction, incompleteness, or objective regression. This does not authorize ignoring explicit authority. Within non-waivable safety and policy boundaries, an explicit informed override remains valid.

Classify material user decisions by impact. A compatible decision may proceed. A trade-off requires a warning and recommendation. A regression requires a strong warning. A decision that contradicts the durable objective stops for explicit informed override. Ambiguity or casual assent is not informed approval for material architecture, protocol, security, compatibility, destructive, or irreversible change.

## Artifact ownership and authority

Canonical target-repository artifacts are:

- `task.yaml`: Architect-owned authority;
- `report.yaml`: Executor-owned evidence;
- `review.yaml`: Architect-owned judgment when repository policy stores it;
- [templates/continuation.yaml](../templates/continuation.yaml): a small machine-readable continuation envelope, not shared mutable state.

Content ownership, authority, and capability availability are distinct. Capability availability never grants authority, and authority never proves capability availability. A known capability is not a currently available capability. No role manufactures another role's authority or evidence.

`task.git_authority` governs Executor Git mutations. `create_branch`, `commit`, `push`, and `promote_to_main` are independent. `commit: true` does not authorize branch creation, push, `main` mutation, or promotion. `push: true` does not authorize branch creation, force push, `main` mutation, or promotion. `promote_to_main: false` forbids `main` ref mutation and merge into `main`. If `create_branch: false`, Executor MUST NOT invoke branch-creation capability for testing, probing, staging, temporary work, backup, recovery, or cleanup. Negative tests use isolated fixtures or mocks, never the live repository.

`task.release_authority`, when present, is separately owned authority with three independent booleans: `create_version_tag`, `mutate_repository_metadata`, and `publish_release`. If absent, all three are false. Commit, push, and `promote_to_main` never imply any release authority.

## Canonical handoffs

[templates/handoff.yaml](../templates/handoff.yaml) is the Architect-to-Executor envelope containing protocol/type, exact task identity/path, repository/branch, and exact `base_head`.

Before mutation Executor verifies supported protocol, `handoff_type == EXECUTOR`, repository/branch identity, live HEAD equality with `base_head`, exact task identity at that commit, task binding, `execution_ready`, pinned skills, structure authority, current-phase capability availability, and applicable mutation authority. Any mismatch is `BLOCKED`.

[templates/continuation.yaml](../templates/continuation.yaml) carries exact identity for a later post-review phase: protocol/task identity, phase, `reviewed_report.commit`, report revision, `promotion_candidate_head`, expected refs, prior result/lifecycle state, and one next authorized action. It does not create authority and does not implement an orchestrator, scheduler, queue, daemon, registry, database, or cross-session messaging runtime.

## Execution base without self-reference

Use `handoff_snapshot`:

1. Architect completes final planning/task changes.
2. Commit planning state when required.
3. Refresh the target branch and capture exact HEAD `H`.
4. Emit the handoff with `target.base_head=H`.
5. Executor reads the task from `H` and requires live HEAD to equal `H` before mutation.

No artifact needs to contain the SHA of the commit containing itself.

## Identity and ownership

Keep these identities distinct:

- `base_head`: Architect handoff identity for the pre-execution task snapshot;
- `final_execution_head`: Executor implementation HEAD before committing `report.yaml`;
- `reviewed_report.commit`: exact commit containing the report an independent Architect actually reviewed;
- `promotion_candidate_head`: accepted-lineage `dev` SHA used for authoritative verification and promotion;
- authoritative verifier identity/result: verifier-owned evidence applying to the exact candidate SHA;
- lifecycle state: a derived conclusion from authoritative artifacts, refs, and evidence, never a shared role-writable state file.

`reviewed_report.commit` must resolve the exact committed report. Normal cross-session remote review requires remote Git reachability. A local-only report commit is valid only when reviewer and Executor use an explicitly **shared trusted** checkout or Git object database that deterministically resolves the same commit and report content.

`report.yaml` state belongs to Executor evidence. It may remain `REPORTED` / `NEEDS_REVIEW` after a separate Architect accepts that exact report. Architect acceptance is separate evidence and does not justify rewriting the Executor report merely to mirror later review state.

## Derived workflow lifecycle

Lifecycle is derived, not assigned by a multi-writer state service:

- `PLANNED`: approved task and exact handoff exist.
- `REPORTED`: Executor has produced the exact report evidence.
- `ACCEPTED`: an independent Architect/session accepted the exact `reviewed_report.commit`.
- `VERIFIED`: the authoritative verifier produced the required result for the exact `promotion_candidate_head`.
- `PROMOTED_NOT_RELEASED`: `main` has been explicitly promoted to the exact accepted candidate, but one or more separately authorized release actions are not completed. Missing release capability does not invalidate the completed promotion.
- `RELEASED`: separately authorized release actions are complete and final identity verification succeeds.

`BLOCKED`, `REVISION_REQUIRED`, and `REVERIFY / REVIEW_REQUIRED` are stop/results, not permission to skip a lifecycle boundary.

## Pre-authorized continuation

Optional `continuation_policy.mode` is one of:

- `MANUAL`: return control after the current bounded phase;
- `AUTO_UNTIL_STOP`: an orchestration environment MAY dispatch the next required independent role or phase without returning to the user when existing exact authority already covers it.

If `continuation_policy` is absent, behavior is `MANUAL`.

`AUTO_UNTIL_STOP` does not merge roles, let Executor self-accept, manufacture verifier PASS, infer promotion/release authority, or treat absence of a human as approval. It stops on `BLOCKED`, `STALE_STATE`, `AUTHORITY_REQUIRED`, `CURRENT_PHASE_CAPABILITY_UNAVAILABLE`, `REVIEW_REQUIRED`, `REVERIFY_REQUIRED`, or `USER_STOP`.

Independent Architect review may be performed by a separate agent/session. Independence means distinct Architect role/session plus exact-evidence separation from the Executor, not a human-only requirement.

## Execution environment and surface selection

Model, effort, and execution surfaces are supplied or established by the operator/environment, not guessed by Architect. Choose the least-powerful currently available surface sufficient for the phase. Use bounded escalation only when an authorized requirement cannot be satisfied on the lesser surface. Capability availability and authority remain separate facts.

## Phase-specific capability preflight

Optional `capability_requirements` maps semantic phases such as `EXECUTION`, `REVIEW`, `VERIFICATION`, `PROMOTION`, and `RELEASE` to required semantic capabilities. Missing declarations grant nothing.

Immediately before the first mutation or authoritative action of the current phase, preflight that phase's required capabilities. If the approved task already knows that native verification or another mandatory current-execution capability is required to complete the current execution, prove that currently available capability before the first mutation. If a required current-phase capability is unavailable, return `CURRENT_PHASE_CAPABILITY_UNAVAILABLE` and block before mutation. Do not preflight later phases as a prerequisite to completing an earlier authorized phase.

Examples: repository content write/test execution for `EXECUTION`; exact commit/report resolution for `REVIEW`; exact-SHA verifier access for `VERIFICATION`; non-force target-ref update for `PROMOTION`; tag, repository-metadata, and release-publication APIs for `RELEASE`.

## GitHub/local drift

Authorized remote Git state is canonical repository truth; local state is an execution copy. A local clean/behind copy may be synchronized when authority permits. Local ahead or local dirty state is divergence or unknown work: never auto-push, reset, delete, or adopt it as authority merely because remote state is canonical. Remote drift from the authorized ref invalidates stale execution authority and fails closed.

## Local Hygiene Contract

Any local execution surface isolates temporary work under one run-owned root. Cleanup is part of completion when the current execution created local temporary artifacts. Cleanup authority is narrower than ordinary filesystem mutation authority: clean only artifacts created by the current run or explicitly disposable runtime-owned state.

Recursive cleanup is legal only when all safety proof is present. The target must be the exact current-run run-owned root or explicitly disposable runtime-owned root; creation, ownership, and run identity must be proven; canonical realpath must be contained in the authorized temporary/runtime root; and the target must not be a symlink traversal. Reject an empty or unresolved target, filesystem root, home, workspace root, repository root, any ancestor of those roots, pre-existing user state, a sibling project, or arbitrary user-supplied cleanup input. Path names, cache-like appearance, proximity to another project, or task/config input alone never prove disposability.

Missing cleanup proof means retain or return `BLOCKED`; never guess and delete. Evidence still required for diagnosis is retained with bounded artifact identity and reason and reported as `RETAINED_FOR_EVIDENCE`. Later stale cleanup obeys the same ownership, identity, realpath, and containment rules. A safely cleaned/no-artifact execution reports `PASS`.

## TASK LAUNCH presentation

TASK LAUNCH is Architect-only operator UX and presentation only. It is not persisted per task, is not execution authority, and Executor does not own it. It contains only Chat, Role, operator-supplied Model, operator-supplied Effort, Progress, and Giải thích / short explanation. Follow it separately with a self-contained `PROMPT TO COPY`. No reusable launch artifact, launcher subsystem, or second authority source is created.

## Promotion lineage after review

Let `R = reviewed_report.commit` after Architect accepts that exact report.

Only two candidate lineages are valid:

1. `promotion_candidate_head == R`; or
2. `promotion_candidate_head` is the **single-parent direct child** of `R`, its only parent is `R`, and that one child commit contains only the expected Architect-owned review artifact.

A merge commit is never the permitted review-artifact child. An empty child is not the expected review artifact. Any other `dev` mutation after `R` invalidates the accepted lineage and requires a new Executor report plus Architect review. This exact accepted-lineage rule is unchanged.

Authoritative verification applies to the exact `promotion_candidate_head`. If `dev` changes afterward, prior evidence is stale: `REVERIFY / REVIEW_REQUIRED`. Actual `dev -> main` promotion is a separate explicitly authorized operation. Release remains separate again.

## Structure authority applicability

Architect owns `structure_authority.status`:

- `RESOLVED`: non-empty source required;
- `NOT_APPLICABLE`: non-empty rationale required and valid only when structure cannot materially change;
- `UNRESOLVED`: execution cannot be ready.

Executor never changes this status to unblock itself.

## Gap policy

`LOCAL` is necessary for current acceptance criteria, completely inside authorized scope, and permitted by task policy. `FOLLOW_UP` is real but unnecessary or unauthorized for the current task; record it and do not fix it. `BLOCKING` means safe continuation requires missing or conflicting authority; stop with evidence. Discovery is never authorization.

## Global structure invariants

No orphan source files. Every new source file belongs to an existing or explicitly authorized responsibility. No speculative scale structure. Do not create layers, factories, registries, plugin systems, services, queues, caches, shared modules, top-level directories, or scaling infrastructure for hypothetical needs.

These unconditional protocol rules need not be recopied as prose into every task. The single canonical v3 task model remains authoritative; there is no task-lite, task-compact, second schema, or second protocol.

## Executor flow

`receive exact handoff → verify base/task/rules → preflight EXECUTION capability → execute restrictive scope → resolve LOCAL only → record FOLLOW_UP → stop on BLOCKING → run checks → local hygiene gate → write REPORTED report → commit/publish report only when separately authorized → stop`

Executor never self-accepts its report.

## Architect review and continuation

An independent Architect/session resolves the exact committed report identified by `reviewed_report.commit` and reviews protocol, identity, execution base, skills, scope, structure, gaps, Git actions, acceptance evidence, and verifier evidence. Outcome is `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`.

`ACCEPTED` is contract acceptance. It is not authoritative verifier PASS, promotion authority, release authority, or proof that those later capabilities are available. When continuation is authorized, emit/use only exact evidence and refs; stale identity fails closed.
