# Task Protocol

This protocol defines reusable Architect-to-Executor governance across repositories. `agent-skills` owns how work is governed; each target repository owns what its product is and stores its live tasks.

Supported protocol version: **3**. Unsupported versions fail closed and are never silently upgraded.

## Core bindings

An Architect session binds to one immutable target repository. External repositories and documentation may be read as references but never become implicit targets. Asking the bound Architect to govern a different target produces `NEW_ARCHITECT_SESSION_REQUIRED`.

An Executor session binds to one approved task revision, one repository, one branch, and one exact execution authorization. It does not execute unrelated work, reinterpret architecture, or broaden scope.

## Artifact ownership and Git authority

Canonical target-repository artifacts are:

- `task.yaml`: Architect-owned authority;
- `report.yaml`: Executor-owned evidence;
- `review.yaml`: Architect-owned judgment when repository policy stores it.

Content ownership and Git mutation authority are distinct. `task.git_authority` applies to Executor Git mutations. Executor may write `report.yaml` content, but an execution-ready task that requires canonical committed report evidence must authorize Executor commit capability. Architect review authority does not inherit Executor Git authority. Conversely, Executor commit authority does not authorize writing Architect-owned review content.

The Executor Git capabilities `create_branch`, `commit`, `push`, and `promote_to_main` are independent. `commit: true` does not authorize branch creation, push, `main` mutation, or promotion. `push: true` does not authorize branch creation, force push, `main` mutation, or promotion. `promote_to_main: false` forbids `main` ref mutation and merge into `main`. If `create_branch: false`, Executor MUST NOT invoke branch-creation capability at all, including for testing, capability probing, staging, temporary work, backup, commit construction, recovery, or cleanup. Negative tests for forbidden Git operations use isolated fixtures or mocks, never the live repository.

An Architect-owned review artifact may remain external when target repository policy permits. No role manufactures another role's authority.

## Canonical Executor handoff

The canonical reusable shape is [templates/handoff.yaml](../templates/handoff.yaml). It is a small authorization/locator envelope containing protocol/type, exact task identity/path, repository/branch, and exact `base_head`.

Before mutation Executor verifies supported protocol, `handoff_type == EXECUTOR`, repository/branch identity, live HEAD equality with `base_head`, exact task identity at that commit, task binding, `execution_ready`, pinned skills, structure authority, and Executor Git authority. Any mismatch means `BLOCKED`.

## Execution base without self-reference

Use `handoff_snapshot`:

1. Architect completes final planning/task changes.
2. Commit planning state when required.
3. Refresh the target branch and capture exact HEAD `H`.
4. Emit the handoff with `target.base_head=H`.
5. Executor reads the task from `H` and requires live HEAD to equal `H` before mutation.

No artifact needs to contain the SHA of the commit containing itself.

## Four SHA identities

Keep these distinct:

- `base_head`: pre-execution authorization and task snapshot;
- `final_execution_head`: last implementation HEAD before committing the report;
- `reviewed_report.commit`: exact commit containing the report Architect reviewed;
- `promotion_candidate_head`: exact `dev` SHA to which authoritative verification applies.

`reviewed_report.commit` must identify a committed report, not an uncommitted working copy or a different report revision.

A report is reviewable only when the Architect review context can deterministically resolve `reviewed_report.commit` and the exact report path/content. The only supported transport is either remote Git reachability or an explicitly shared trusted Git object/checkout environment. For normal cross-chat or otherwise remote-only review, the report commit must be reachable from the authorized remote Git state. A local-only report commit is valid only when the Architect review context shares that trusted checkout/object database and can resolve the same object deterministically. `commit` and `push` remain independent: `commit: true` does not imply push, and remote reachability must be granted with only the minimum authorized push capability when the intended review transport requires it. An execution-ready task must not knowingly select a canonical report lifecycle that its intended Architect review context cannot consume. `commit: false` cannot support a claim of canonical committed report evidence.

## Promotion lineage after review

Let `R = reviewed_report.commit` after Architect accepts that exact report.

Only two candidate lineages are valid:

1. `promotion_candidate_head == R`; or
2. `promotion_candidate_head` is the **single-parent direct child** of `R`, its only parent is `R`, and that one child commit contains only the expected Architect-owned review artifact.

A merge commit is never the permitted review-artifact child. An empty child is not the expected review artifact. Any other `dev` mutation after `R` invalidates the accepted lineage and requires a new Executor report plus Architect review. This includes implementation, unrelated documentation, cleanup, dependency changes, another task's commit, unrelated commits, or a second post-review commit.

The previous broad idea of “all other intended release mutations” is deliberately not authority. If a mutation is not the single permitted review-artifact child, accepted lineage no longer covers it.

Authoritative verification applies to the exact `promotion_candidate_head`. If `dev` changes afterward, the prior evidence is stale: `REVERIFY / REVIEW_REQUIRED`. Actual `dev -> main` promotion remains a separate explicitly authorized operation.

## Structure authority applicability

Architect owns `structure_authority.status`:

- `RESOLVED`: non-empty source required;
- `NOT_APPLICABLE`: non-empty rationale required and valid only when structure cannot materially change;
- `UNRESOLVED`: execution cannot be ready.

Executor never changes this status to unblock itself.

## Gap policy

### LOCAL

Necessary for current acceptance criteria, completely inside authorized scope, and permitted by `local_auto_fix`. No architecture/spec/public-contract/dependency/unauthorized-structure boundary may be crossed.

### FOLLOW_UP

Real but unnecessary for the current task or outside current authorization. Record evidence and do not fix it.

### BLOCKING

Safe continuation requires missing or conflicting Architect authority. Stop and report evidence.

Discovery is never authorization.

## No orphan source files

Every new source file must belong to an existing or explicitly authorized feature, domain, component, layer, or infrastructure responsibility. Generic dumping grounds are not justified by convenience.

## No speculative scale structure

Do not create layers, factories, registries, plugin systems, services, queues, caches, shared modules, top-level directories, or scaling infrastructure for hypothetical future needs.

Prefer `existing solution → localized change → small local abstraction → larger abstraction → subsystem` and move right only with current evidence or explicit authority.

## Executor flow

`receive handoff → verify exact base/task/rules → verify structure and Git authority → execute restrictive scope → resolve LOCAL only → record FOLLOW_UP → stop on BLOCKING → run checks → write report → commit report only when task.git_authority permits → publish only when separately authorized and required by review transport → stop`

## Architect review flow

Architect reviews the exact committed report identified by `reviewed_report.commit`, including protocol, identity, execution base, skills, scope, structure, gaps, Git actions, acceptance evidence, and verifier evidence. Architect outcome is `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`.

`ACCEPTED` is contract acceptance. It is not authoritative verifier PASS and not promotion authorization.
