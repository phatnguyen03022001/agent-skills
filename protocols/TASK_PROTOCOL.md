# Task Protocol

This protocol defines reusable governance for Architect-to-Executor work across repositories. `agent-skills` owns **how work is governed**; each target repository owns **what its product is** and stores its live tasks.

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

## Execution base without self-reference

A committed `task.yaml` must not contain the exact SHA of the commit that contains itself. Writing that SHA would create a self-referential loop.

Use `handoff_snapshot`:

1. Architect completes planning/task changes.
2. Commit the final planning state to the target branch when required.
3. Refresh the branch and capture exact HEAD `H`.
4. Emit an external copy/paste `EXECUTOR_HANDOFF` that contains `H` as `base_head`.
5. Executor verifies live HEAD equals `H` and reads the task from `H` before mutation.

The handoff is an execution authorization envelope, not a file that must be committed back into the same branch.

Example:

```yaml
EXECUTOR_HANDOFF:
  task:
    id: TASK-0001
    revision: 1
    path: .agent/tasks/TASK-0001/task.yaml
  target:
    repository: owner/repo
    branch: dev
    base_head: <exact HEAD captured after final planning commit>
  skill_library:
    repository: phatnguyen03022001/agent-skills
    revision: <exact immutable SHA>
```

A report uses the analogous rule: `final_execution_head` means the last implementation HEAD before committing the report artifact. Architect identifies the report to review by exact report commit/path. No artifact needs to contain its own commit SHA.

## Skill determinism and progressive disclosure

Architect first inspects skill names/descriptions, then loads only candidate bodies. Normally use 2–5 skills; more than about seven is a review/decomposition signal.

`architect_analysis_skills` record reasoning provenance only. They do not automatically enter Executor context.

`execution_skills.required` must be resolved and obeyed by Executor. Missing required skills block execution. `execution_skills.recommended` are non-blocking, do not broaden scope, and cannot reinterpret the approved task.

Shared internal skills use one library-level exact commit revision. External skills must carry exact `name`, `source`, and immutable `revision`. Executor must not silently substitute newer rules.

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

A typo in already-authorized code can be LOCAL when fixing it is necessary to complete the task.

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

File names must communicate responsibility according to target language/framework/project conventions. Challenge names such as `new_service.py`, `service2.ts`, `helpers.go`, `misc.py`, `temp.ts`, or `processor_new.go` unless project convention makes them meaningful. Do not impose a universal naming regex.

### Structure authorization

Tasks may enumerate expected new files and purpose. Unlisted new files default forbidden. Architect may explicitly grant small implementation-local decomposition with bounded `max`, `within`, and `purpose`. This does not authorize repository redesign.

Executor reports structural concerns outside scope as `structural_observations`; Architect decides whether they become follow-up tasks.

## No speculative scale structure

Do not create layers, factories, registries, plugin systems, extension points, interfaces, services, queues, caches, shared modules, top-level directories, or scaling infrastructure for hypothetical future needs.

Prefer:

`existing solution → localized change → small local abstraction → larger abstraction → subsystem`

Move right only when current evidence or explicit project authority proves the simpler option insufficient.

## Architect task creation flow

`user intent → bind one target repo → inspect project authority/vision/structure → refresh branch → discover skill metadata → load minimal analysis skills → resolve material product/spec/design gaps → author planning artifacts if authorized → create/revise task → commit planning state if required → capture fresh execution base → emit self-contained Executor handoff`

A fresh Executor must need no hidden previous-chat context.

## Executor flow

`receive one handoff → verify task identity → verify repo/branch/base → verify pinned skill rules → verify required execution skills → verify structure authority → verify Git/worktree authority → execute restrictive scope → resolve LOCAL only → record FOLLOW_UP → stop on BLOCKING → run mandatory checks → write report → stop`

## Architect review flow

Architect reviews exact report identity, execution base, skill revision, acceptance evidence, changed/new files, structure authorization, gap classification, product/spec/vision drift, Git actions, and verifier evidence.

Architect outcome is `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`. Architect may create follow-up tasks from discovered gaps but must never rewrite Executor evidence.

Promotion readiness is reviewed separately; actual promotion requires explicit authority and fresh branch state.
