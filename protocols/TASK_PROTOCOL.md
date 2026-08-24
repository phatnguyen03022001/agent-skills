# Task Protocol

This protocol defines reusable governance for Architect-to-Executor work across repositories. `agent-skills` owns **how work is governed**; each target repository owns **what its product is** and stores its live tasks.

Supported protocol version: **3**. Unsupported versions fail closed; they are never silently upgraded.

## Core bindings

### One Architect session → one target repository

An Architect session binds to exactly one immutable target repository. It may read external repositories, upstream source, dependencies, specifications, or documentation as references. Reference repositories never become implicit execution targets.

If a bound Architect is asked to govern or execute work for a different target repository, the semantic outcome is `NEW_ARCHITECT_SESSION_REQUIRED`.

### One Executor session → one task revision → one repository

An Executor session binds to exactly one approved task revision, one target repository, one branch, and one execution authorization. It must not execute unrelated tasks, switch targets, reinterpret project architecture, or broaden scope.

## Project authority versus skills

Target repositories own project-specific authority: product intent, roadmap, specifications, architecture/design decisions, structure conventions, code, deployment policy, and verification authority. Exact file names are project-defined; `PRODUCT.md`, `ROADMAP.md`, `spec/`, `design/`, or `STRUCTURE.md` are examples, not mandates.

Skills teach reusable methods for reasoning and execution. Shared skills must not contain another project's live product vision.

When explicitly authorized, Architect may author planning/authority artifacts in the target repository. Executor may author only implementation-scoped artifacts authorized by the task. Project-designated verifier owns authoritative PASS/FAIL.

## Target task storage

At current scale, the target repository task directory is the task list:

```text
.agent/tasks/
  TASK-0001/
    task.yaml
    report.yaml
    review.yaml
  TASK-0002/
    task.yaml
```

Do not add a task database, generated registry, search service, queue, or coordinator without observed scale friction. A generated index may become justified only when directory enumeration and repository search no longer provide acceptable discovery.

Artifact ownership is strict:

- `task.yaml`: Architect-owned authority. Executor never rewrites it.
- `report.yaml`: Executor-owned evidence. Architect never rewrites it.
- `review.yaml`: Architect-owned review decision.

Git history preserves artifact changes. Meaningful task changes increment `task_revision`; never silently overwrite task meaning.

## Small state model

Logical flow:

`DRAFT → READY → EXECUTING → REPORTED → ACCEPTED`

Exceptional transitions:

- `DRAFT | READY | EXECUTING → BLOCKED`
- `REPORTED → REVISION_REQUIRED | BLOCKED`
- `REVISION_REQUIRED → DRAFT` as a new task revision
- `BLOCKED → REVISION_REQUIRED` when Architect can resolve the blocker

Ownership prevents roles from fighting over one mutable status field: task normally carries `DRAFT/READY`, Executor session/report establishes `EXECUTING/REPORTED/BLOCKED`, and Architect review records `ACCEPTED/REVISION_REQUIRED/BLOCKED`.

## Canonical Executor handoff

The canonical reusable shape is [templates/handoff.yaml](../templates/handoff.yaml). It is deliberately a small authorization/locator envelope:

```yaml
protocol_version: 3
handoff_type: EXECUTOR
task:
  id: TASK-0001
  revision: 1
  path: .agent/tasks/TASK-0001/task.yaml
target:
  repository: owner/repo
  branch: dev
  base_head: <exact HEAD captured after final planning commit>
```

The handoff does **not** duplicate scope, acceptance criteria, skill rules, structure policy, or authority sources. Those remain authoritative in `task.yaml` at the exact pinned base.

Before mutation Executor verifies, in order:

1. supported `protocol_version`;
2. `handoff_type == EXECUTOR`;
3. repository and branch match the execution session;
4. live branch HEAD equals handoff `target.base_head`;
5. `task.path` exists at that exact commit and is read from that commit;
6. task ID/revision equal handoff ID/revision;
7. task `architect_binding.target_repository` and `target.repository` both equal the handoff repository;
8. task is `execution_ready=true`;
9. task-pinned skill library and required execution rules resolve;
10. structure and Git/worktree authority permit execution.

Any mismatch means `BLOCKED`. Never refresh the handoff, read a newer task because the branch moved, repair an unsupported protocol, or substitute newer rules.

## Execution base without self-reference

A committed `task.yaml` must not contain the exact SHA of the commit that contains itself.

Use `handoff_snapshot`:

1. Architect completes planning/task changes.
2. Commit final planning state when required.
3. Refresh the target branch and capture exact HEAD `H`.
4. Emit the canonical external handoff with `target.base_head=H`.
5. Executor verifies live HEAD equals `H` and reads the task from `H`.

The handoff is an execution authorization envelope, not a file that must be committed back into the same branch.

A report uses the analogous rule: `final_execution_head` means the last implementation HEAD before committing the report artifact. The report commit is identified externally during Architect review. No artifact needs to contain its own commit SHA.

## Skill determinism and progressive disclosure

Architect first inspects skill names/descriptions, then loads only candidate bodies. Normally use 2–5 skills; more than about seven is a review/decomposition signal.

`architect_analysis_skills` record reasoning provenance only. They do not automatically enter Executor context.

`execution_skills.required` must be resolved and obeyed by Executor. Missing required skills block execution. `execution_skills.recommended` are non-blocking, do not broaden scope, and cannot reinterpret the approved task.

Shared internal skills use one library-level exact commit revision. External skills must carry exact `name`, `source`, and immutable `revision`. Executor must not silently substitute newer rules.

## Structure authority applicability

Architect owns the decision; Executor may not change it to unblock execution.

`structure_authority.status` is exactly one of:

- `RESOLVED`: `source` is required. Executor follows that authority.
- `NOT_APPLICABLE`: `rationale` is required. Valid only when the task cannot materially affect repository/module/file structure.
- `UNRESOLVED`: fail closed. The task cannot be execution-ready.

`NOT_APPLICABLE` is suitable for work such as a README typo when no repository/module/file structure can materially change. It is invalid for source-file creation, module moves, dependency-boundary changes, new top-level/shared areas, or structural reorganization.

Regardless of status, no-orphan-file, naming/ownership, unauthorized-structure, and no-speculative-scale rules remain protocol invariants whenever relevant.

## Gap policy

Executor classifies every material discovered gap as exactly one of:

### LOCAL

May be resolved only when all are true:

- necessary to satisfy current acceptance criteria;
- completely inside authorized scope;
- no architecture change;
- no canonical spec/roadmap change;
- no public-contract broadening;
- no unauthorized dependency change;
- no unauthorized structural boundary;
- task permits `local_auto_fix`.

### FOLLOW_UP

The issue is real but not required for the current task or outside current authorization. Record evidence and do not fix it. Architect may later create a follow-up task with lineage:

```yaml
origin:
  type: discovered_gap
  task_id: TASK-0001
  gap_id: GAP-001
```

### BLOCKING

Safe/correct continuation requires missing or conflicting authority, specification, design, security, structure, dependency, or public-contract decision. Stop and report evidence. Executor never converts discovery into implicit authorization.

## Always-on scope discipline

Task approval never implies:

- unrelated cleanup or adjacent fixes;
- speculative features or roadmap expansion;
- undocumented scope expansion;
- architecture or canonical-spec drift;
- dependency upgrades/additions;
- structural reorganization;
- “while I'm here” refactors.

These are core protocol invariants, not optional skill advice.

## Structure authority

Each target repository should have one canonical source for structure rules when structure matters. Use an existing authoritative document if one exists; otherwise Architect may define a project-specific structure artifact when explicitly authorized. Do not force one universal filename or layout.

Structure authority should cover relevant module/feature/domain ownership, permitted roots, dependency direction, source/generated/test placement, legitimate shared areas, new top-level directory rules, project language/framework conventions, naming conventions, and decisions requiring Architect approval.

Feature/domain/component ownership is the default principle where compatible with the project. Physical placement follows target conventions: Go, Python, TypeScript, and other ecosystems need not look alike.

### No orphan source files

Every new source file must belong to an existing or explicitly authorized feature, domain, component, layer, or infrastructure responsibility.

Do not casually create generic dumping grounds such as `utils`, `helpers`, `common`, `misc`, or `shared`. They are allowed only when cross-domain ownership is real and justified by target architecture.

File names must communicate responsibility according to target language/framework/project conventions. Do not impose a universal naming regex.

### Structure authorization

Tasks may enumerate expected new files and purpose. Unlisted new files default forbidden. Architect may explicitly grant small implementation-local decomposition with bounded `max`, `within`, and `purpose`. This does not authorize repository redesign.

Executor reports structural concerns outside scope as `structural_observations`; Architect decides whether they become follow-up tasks.

## No speculative scale structure

Do not create layers, factories, registries, plugin systems, extension points, interfaces, services, queues, caches, shared modules, top-level directories, or scaling infrastructure for hypothetical future needs.

Prefer:

`existing solution → localized change → small local abstraction → larger abstraction → subsystem`

Move right only when current evidence or explicit project authority proves the simpler option insufficient.

## Architect task creation flow

`user intent → bind one target repo → inspect project authority/vision/structure → refresh branch → discover skill metadata → load minimal analysis skills → resolve material product/spec/design gaps → author planning artifacts if authorized → create/revise task → resolve structure authority applicability → commit planning state if required → capture fresh execution base → emit canonical handoff`

Architect must not emit an execution-ready task/handoff with an unsupported protocol version. A fresh Executor must need no hidden previous-chat context.

## Executor flow

`receive one handoff → verify protocol/type → verify repo/branch/base → load exact task at base → verify task identity/binding → verify pinned skill rules → verify structure authority → verify Git/worktree authority → execute restrictive scope → resolve LOCAL only → record FOLLOW_UP → stop on BLOCKING → run mandatory checks → write report → stop`

## Architect review flow

Architect reviews exact report identity, protocol version, execution base, skill revision, acceptance evidence, changed/new files, structure authorization, gap classification, product/spec/vision drift, Git actions, and verifier evidence.

Architect outcome is `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`. Architect may create follow-up tasks from discovered gaps but must never rewrite Executor evidence.

`ACCEPTED` is contract acceptance, not authoritative verifier PASS and not promotion authorization.

## Promotion candidate and exact-SHA verification

These identities are intentionally different:

- handoff `base_head`: pre-execution authorization/task snapshot;
- report `final_execution_head`: implementation HEAD before report commit;
- `reviewed_report.commit`: exact commit containing the report reviewed by Architect;
- `promotion_candidate_head`: final `dev` SHA after **all repository mutations intended for promotion**.

Promotion sequence:

`implementation → report commit if required → Architect review → review commit if required → refresh dev → capture promotion_candidate_head H → authoritative verification of exact H → no further dev mutation → explicit promotion decision → promote exact H`

Verification evidence should live outside the candidate commit when recording it would mutate `dev` after verification.

A small external authorization envelope is sufficient when needed:

```yaml
PROMOTION_AUTHORIZATION:
  protocol_version: 3
  repository: owner/repo
  from_branch: dev
  to_branch: main
  promotion_candidate_head: "<exact SHA>"
  verification:
    mechanism: ""
    expected_signal: ""
    result: PASS
    evidence: ""
  authorized: true
```

Before promotion, candidate `H` must still be current `dev` HEAD, must satisfy project ancestry/divergence policy against intended `main`, and required authoritative verification must explicitly apply to `H`.

If `dev` changes after verification, the prior verification/authorization does not cover the new HEAD: `REVERIFY / REVIEW_REQUIRED`. Do not verify `H`, commit a “verification passed” artifact producing `H+1`, then promote `H+1` without re-verifying.

Actual promotion remains a separate explicitly authorized operation.
